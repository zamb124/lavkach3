from starlette.requests import Request

from app.front.apps.inventory.views import StoreStaffView


async def get_user_store(request: Request):
    store_staff_model = request.scope['env']['store_staff']
    async with store_staff_model.adapter as a:
        data = await a.list(params={'user_id': request.user.user_id})
        store_staff = data['data'][0]
        store_staff_cls = StoreStaffView(request)
        await store_staff_cls.init(params={'store_id': store_staff['store_id']})
    return store_staff_cls

