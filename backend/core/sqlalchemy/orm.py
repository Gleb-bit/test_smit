from typing import Union, Any, Sequence

from sqlalchemy import select, Result, Row, RowMapping, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, RelationshipProperty


class Orm:

    @staticmethod
    def get_mtm_fields(table):
        mtm_fields = []
        for field_name, field in table.__mapper__.relationships.items():
            if isinstance(field, RelationshipProperty) and field.secondary is not None:
                mtm_fields.append(field_name)

        return mtm_fields

    @staticmethod
    def get_related_fields_dict(table, data: dict):
        result = {}

        for field_name, relation in table.__mapper__.relationships.items():
            if (
                isinstance(relation, RelationshipProperty)
                and relation.secondary is not None
            ):
                related_model = relation.mapper.class_
                if field_name in data:
                    result[(related_model, field_name)] = data[field_name]

        return result

    @staticmethod
    def get_related_field(table, related_table):
        for field_name, relationship in table.__mapper__.relationships.items():
            if (
                isinstance(relationship, RelationshipProperty)
                and relationship.mapper.class_ == related_table
            ):
                return relationship

    @staticmethod
    def get_query_with_relations(query, relations="*", join=False):
        return query.options(selectinload(relations))

    @staticmethod
    def exclude_mtm_fields(table, data: dict):
        mtm_fields = {
            field_name
            for field_name, relation in table.__mapper__.relationships.items()
            if isinstance(relation, RelationshipProperty)
            and relation.secondary is not None
        }
        return {key: value for key, value in data.items() if key not in mtm_fields}

    @classmethod
    async def all(
        cls, table, session: AsyncSession, relations=None
    ) -> Sequence[Row[Any] | RowMapping | Any]:
        """
        Method to retrieve all records for the specified table.

        :param:
        - `table`: SQLAlchemy table.
        - `session`: SQLAlchemy asynchronous session.
        - `relations`: related fields.

        :return:
         `List of all records for the table.`
        """

        query = select(table)

        if relations:
            query = cls.get_query_with_relations(query, relations)

        execution = await session.execute(query)

        return execution.scalars().all()

    @classmethod
    async def create(cls, table, data: dict, session: AsyncSession):
        """
        Method to create the instance in the table based on a dictionary of fields.

        :param:
        - `table`: SQLAlchemy table.
        - `data`: Dictionary with table data.
        - `session`: SQLAlchemy asynchronous session.

        :return:
            `Created object.`
        """

        instance = table(**cls.exclude_mtm_fields(table, data))
        session.add(instance)

        await session.commit()
        await session.refresh(instance)

        return instance

    @classmethod
    async def filter_by(
        cls,
        table,
        filter_data: dict,
        session: AsyncSession,
        exclude_data: dict = None,
        relations=None,
        join=False,
    ) -> Result:
        """
        Method to filter records in the table based on a dictionary of fields.

        :param:
        - `table`: SQLAlchemy table.
        - `filter_data`: Dictionary with filter conditions.
        - `session`: SQLAlchemy asynchronous session.
        - `relations`: related fields.

        :return:
            `Query result filtered by the dictionary fields.`
        """

        query = select(table).filter_by(**filter_data)

        if relations:
            query = cls.get_query_with_relations(query, relations)

        if join:
            query = query.join(relations)

        if exclude_data:
            exclude_query = select(table).filter_by(**exclude_data)
            query = query.except_(exclude_query)

        return await session.execute(query)

    @classmethod
    async def insert(cls, table, data: list, session: AsyncSession, return_data=None):
        """
        Method to insert data in the table based on a dictionary of fields.

        :param:
        - `table`: SQLAlchemy table.
        - `data`: Dictionary with table data.
        - `session`: SQLAlchemy asynchronous session.
        - `return_data`: Fields to return after insert.

        :return:
            `ids of inserted objects.`
        """
        if not return_data:
            return_data = table.id

        stmt = insert(table).values(data).returning(return_data)

        result = await session.execute(stmt)
        await session.commit()

        return result

    @classmethod
    async def scalar(
        cls,
        table,
        session: AsyncSession,
        filters: Union[dict, bool] = dict,
        relations=None,
        join=False,
        exclude_data=None,
    ):
        """
        Method to execute a query and retrieve a single record from the table based on filter conditions.

        :param:
        - `table`: SQLAlchemy table to query.
        - `session`: SQLAlchemy asynchronous session.
        - `filters`: Dictionary or boolean condition for filtering (default is empty dictionary).
        - `relations`: related fields.

        :return:
            `First field value from the first row of the query result, or None if no record is found.`
        """

        if isinstance(filters, dict):
            query = await cls.filter_by(
                table, filters, session, exclude_data, relations, join
            )
        else:
            query = await cls.where(table, filters, session, relations, join)

        return query.scalar()

    @staticmethod
    async def update(obj, data: dict, session: AsyncSession):
        for key, value in data.items():
            setattr(obj, key, value)

        await session.commit()

    @staticmethod
    async def update_field(
        table, update_fields: dict, session: AsyncSession, filter_expr=None
    ):
        stmt = update(table)
        if filter_expr:
            stmt = stmt.where(filter_expr)

        await session.execute(stmt.values(**update_fields))
        await session.commit()

    @classmethod
    async def where(
        cls,
        table,
        filter_expr,
        session: AsyncSession,
        relations=None,
        join=False,
        execute=True,
    ) -> Result:
        """
        Method to filter records in the table based on a filter expression.

        :param:
        - `table`: SQLAlchemy table.
        - `filter_expr`: SQLAlchemy expression or boolean condition.
        - `session`: SQLAlchemy asynchronous session.
        - `relations`: related fields.

        :return:
            `Query result filtered by the given expression.`
        """
        query = select(table)
        if relations:
            query = cls.get_query_with_relations(query, relations)

        if join:
            query = query.join(relations)

        if execute:
            return await session.execute(query.where(filter_expr))
        else:
            return query.where(filter_expr)
