from lib2to3.fixes.fix_input import context

from django.core.mail import EmailMessage
from olx import settings
import csv
import json
    
def send_review_email(queryset,email):
    
    with open('./sample.csv','w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(["title","price","description","location","owner_name","details","extra"]) 
        for ad in queryset:
            writer.writerow([ad.title,ad.price,ad.description,ad.location,ad.owner_name,json.dumps(ad.details),ad.extra]) 
                 



    # email_subject= 'You can find below the sample'
    # email_body = render_to_string('email_message.txt',context)


    mail= EmailMessage(
        'testsubject',
        'Here is you sample',
        settings.DEFAULT_FROM_EMAIL,[email,],
    )
    mail.attach_file('./sample.csv')
    mail.send(fail_silently=False)
    return True
