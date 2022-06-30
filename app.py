from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from datetime import datetime
from calendar import monthrange
from moneyed import Money, EUR
from ics import Calendar, Event
import json

from dateutil.relativedelta import relativedelta

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/json")
def endpoint_json():
    subs = load_subs_from_json("subs.json")
    return {
        "subs": [sub.json for sub in subs],
        "total": sum([sub.cost for sub in subs]).amount,
    }


@app.get("/calendar")
def endpoint_calendar():
    subs = load_subs_from_json("subs.json")
    c = Calendar()

    for sub in subs:
        e = Event()
        e.name = f"💸 Si rinnova {sub.name} a {sub.cost}"
        e.begin = sub.next_date
        c.events.add(e)

    return PlainTextResponse(str(c))


def load_subs_from_json(path):
    with open(path) as f:
        subs = []
        for sub in json.load(f):
            subs.append(Subscription(sub["name"], sub["cost"], sub["date_start"]))
        return subs


class Subscription:
    def __init__(self, name, cost, date_start, shared=None):
        self.name = name
        self.cost = Money(cost, EUR)
        self.date_start = datetime.strptime(date_start, "%d/%m/%Y")
        self.shared = shared

    @property
    def next_date(self):
        today = datetime.today()
        next_date = today + relativedelta(months=1)
        next_month_len = monthrange(next_date.year, next_date.month)[1]

        if self.date_start.day > next_month_len:
            next_date = next_date.replace(day=next_month_len)
        else:
            next_date = next_date.replace(day=self.date_start.day)

        return next_date

    @property
    def json(self):
        return {
            "name": self.name,
            "cost": self.cost.amount,
            "date_start": self.date_start.strftime("%d/%m/%Y"),
            "next_date": self.next_date.strftime("%d/%m/%Y"),
        }
