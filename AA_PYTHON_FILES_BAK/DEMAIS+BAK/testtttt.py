from datetime import date
from datetime import timedelta

tomorrow = date.today() + timedelta(days=1)
tomorrow = tomorrow.strftime('%d-%m-%Y')
print(tomorrow)