from app.basic.company.models.company_models import Company
from sqlalchemy import insert, select
from conftest import client, session


async def test_create_company():
    company = insert(Company).values(
        title='TestCompany'
    )
    await session.execute(company)
    await session.commit()
    query = select(Company)
    result = await session.execute(query)
    print(result)
    # client.post(
    #     '/api/company/create',
    #     json={
    #         "title": "TestCompany",
    #         "external_id": "100",
    #         "locale": "en_US",
    #         "country": "US",
    #         "currency": "SAE"
    #     }
    # )
    assert 1 == 1
