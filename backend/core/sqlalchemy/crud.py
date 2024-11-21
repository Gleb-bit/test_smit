from typing import Optional

from fastapi import HTTPException, Response
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.sqlalchemy.orm import Orm


class Crud:
    def __init__(self, table):
        self.table = table

    def get_not_found_text(self, obj_id: int):
        return f"{self.table.__name__} with ID №{obj_id} not found"

    @staticmethod
    def get_unique_fields(table):
        return [column.name for column in table.__table__.columns if column.unique]

    @staticmethod
    async def check_field_unique(
        table, data: dict, field: str, session: AsyncSession, obj_id=None
    ):
        async with session.begin():
            field_value = data.get(field)
            filter_data = {field: field_value}
            exclude_data = {"id": obj_id} if obj_id else None

            query = await Orm.filter_by(table, filter_data, session, exclude_data)

            if query.scalar() is not None:
                raise HTTPException(
                    400, f"{table.__name__} with {field}={field_value} already exists"
                )

    @classmethod
    async def check_unique_fields(
        cls, table, data: dict, session: AsyncSession, obj_id=None
    ):
        unique_fields = cls.get_unique_fields(table)

        for field in unique_fields:
            await cls.check_field_unique(table, data, field, session, obj_id)

    async def create(self, data, session: AsyncSession, relations=None):
        """
        Method that creates a new instance of the table

        :param:
        - `data`: Dictionary with data to create a new record.
        - `session`: The current database session.

        :return:
            `Created object.`
        """
        model_dump = data.model_dump()

        await self.check_unique_fields(self.table, model_dump, session)

        instance = await Orm.create(self.table, model_dump, session)

        if relations:
            instance = await Orm.scalar(
                self.table, session, self.table.id == instance.id, relations
            )

        if nested_data := Orm.get_related_fields_dict(self.table, model_dump):
            instance = await self.create_nested(instance, session, nested_data)

        return instance

    async def create_nested(self, instance, session: AsyncSession, nested_data: dict):
        nested_fields = Orm.get_mtm_fields(self.table)

        for table_and_field, data in nested_data.items():
            for nested_obj in data:
                nested_table, nested_field_name = table_and_field

                nested_instance = nested_table(**nested_obj)
                nested_field = getattr(instance, nested_field_name)
                nested_field.append(nested_instance)

        await session.commit()
        await session.refresh(instance, nested_fields)

        load_fields = [
            joinedload(getattr(self.table, field)) for field in nested_fields
        ]
        query = (
            select(self.table).options(*load_fields).where(self.table.id == instance.id)
        )

        result = await session.execute(query)
        return result.scalar()

    async def create_bulk(
        self, data, bulk_key: str, session: AsyncSession, return_data=None
    ):
        data_list = data.model_dump()[bulk_key]

        result = await Orm.insert(self.table, data_list, session, return_data)
        return {bulk_key: [{"id": row[0]} for row in result.fetchall()]}

    async def delete(
        self,
        obj_id: int,
        session: AsyncSession,
        status: int = 204,
        content: dict = None,
    ):
        """
        Method that deletes the instance of the table

        :param:
        - `obj_id`: ID of the instance to delete.
        - `session`: The current database session.

        :return:
            `Response(204).`
        """
        book = await Orm.scalar(self.table, session, self.table.id == obj_id)

        if not book:
            raise HTTPException(404, self.get_not_found_text(obj_id))

        await session.delete(book)
        await session.commit()

        return Response(content=content, status_code=status)

    async def list(
        self,
        session: AsyncSession,
        relations=None,
        sort_field: Optional[str] = None,
        sort_order: Optional[str] = "asc",
        **filters,
    ):
        """
        Метод для получения списка объектов с фильтрацией и сортировкой.

        :param session: Текущая сессия базы данных.
        :param relations: Связанные поля.
        :param sort_field: Поле для сортировки.
        :param sort_order: Порядок сортировки ('asc' или 'desc').
        :param filters: Произвольные параметры для фильтрации.

        :return: Список объектов с примененными фильтрацией и сортировкой.
        """

        query = select(self.table)

        for field, value in filters.items():
            if value is not None:
                query = query.filter(getattr(self.table, field) == value)

        if sort_field or sort_order:
            sort_field = sort_field or "id"
            sort_column = getattr(self.table, sort_field, None)

            if sort_column:
                order = (
                    asc(sort_column)
                    if sort_order.lower() == "asc"
                    else desc(sort_column)
                )
                query = query.order_by(order)

        if relations:
            query = Orm.get_query_with_relations(query, relations)

        execution = await session.execute(query)
        return execution.scalars().all()

    async def retrieve(self, obj_id: int, session: AsyncSession, relations=None):
        """
        Method that retrieves an instance of the table by ID

        :param:
        - `obj_id`: ID of the instance to retrieve.
        - `session`: The current database session.

        :return:
            `Object instance.`
        """
        obj = await Orm.scalar(self.table, session, self.table.id == obj_id, relations)
        if not obj:
            raise HTTPException(404, self.get_not_found_text(obj_id))

        return obj

    async def update(
        self, data: dict, obj_id: int, session: AsyncSession, relations=None
    ):
        """
        Method that updates an instance of the table

        :param:
        - `data`: Dictionary with updated data.
        - `obj_id`: ID of the instance to update.
        - `session`: The current database session.

        :return:
            `Updated object.`
        """
        await self.check_unique_fields(self.table, data, session, obj_id)

        obj = await Orm.scalar(self.table, session, self.table.id == obj_id, relations)

        if not obj:
            raise HTTPException(404, self.get_not_found_text(obj_id))

        await Orm.update(obj, data, session)
        await session.refresh(obj)

        return obj
