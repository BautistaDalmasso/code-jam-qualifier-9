import typing
from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    scope: typing.Mapping[str, typing.Any]

    receive: typing.Callable[[], typing.Awaitable[object]]
    send: typing.Callable[[object], typing.Awaitable[None]]


class RestaurantManager:
    def __init__(self):
        """Instantiate the restaurant manager.

        This is called at the start of each day before any staff get on
        duty or any orders come in. You should do any setup necessary
        to get the system working before the day starts here; we have
        already defined a staff dictionary.
        """
        self.staff = {}
        self.orders_completed = {}

    async def __call__(self, request: Request):
        """Handle a request received.

        This is called for each request received by your application.
        In here is where most of the code for your system should go.

        :param request: request object
            Request object containing information about the sent
            request to your application.
        """

        match request.scope["type"]:
            case "staff.onduty":
                self.staff[request.scope["id"]] = request
                self.orders_completed[request.scope["id"]] = 0
            case "staff.offduty":
                del self.staff[request.scope["id"]]
                del self.orders_completed[request.scope["id"]]
            case "order":
                await self.handle_order(request)


    async def handle_order(self, request: Request):
        selected_chef = self.select_staff(request.scope["speciality"])

        full_order = await request.receive()
        await selected_chef.send(full_order)

        result = await selected_chef.receive()
        await request.send(result)


    def select_staff(self, speciality: str) -> Request:
        """Returns a valid staff member with the least orders completed. """
        valid_staff = list(filter(lambda id_ : (speciality in self.staff[id_].scope["speciality"]), self.staff.keys()))
        least_worked = min(valid_staff, key=self.orders_completed.get)

        self.orders_completed[least_worked] += 1
        return self.staff[least_worked]