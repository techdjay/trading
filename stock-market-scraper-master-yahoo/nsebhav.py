p1 = 'https://www1.nseindia.com/content/historical/EQUITIES/'
p4 = 'bhav.csv.zip\n'

months = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']

days = []

for day in range(1, 32):
    if len(str(day)) == 1:
        days.append('0' + str(day))
    else:
        days.append(str(day))

with open('all_links_file', 'a') as f:
    for yr in range(2006,2021):
        for month in months:
            for day in days:
                f.write(p1+str(yr)+'/'+month+'/cm'+day+month+str(yr)+p4)