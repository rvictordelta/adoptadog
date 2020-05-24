from selenium import webdriver
import pandas as pd
import re

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from creds import u, p, recipients


def dog_scrape():
    # go to shell website to get authkey
    url = "https://wright-wayrescue.org/adoptable-dogs"
    driver = webdriver.Chrome()
    driver.get(url)
    target = driver.find_element_by_class_name("main-content")
    target_str = target.get_attribute('innerHTML')

    # extracte auth key
    try:
        found = re.search('authkey=(.+?)&', target_str).group(1)
    except AttributeError:
        # AAA, ZZZ not found in the original string
        found = '' # apply your error handling

    # go to target petango website with the authkey
    petango_url = f"https://ws.petango.com/webservices/adoptablesearch/wsAdoptableAnimals.aspx?species=Dog&gender=A&agegroup=OverYear&location=&site=&onhold=A&orderby=name&colnum=3&css=http://ws.petango.com/WebServices/adoptablesearch/css/styles.css&authkey={found}&recAmount=&detailsInPopup=No&featuredPet=Include&stageID=&wmode=opaque"
    driver.get(petango_url)
    # extract dog info
    dogs = driver.find_elements_by_tag_name("td")
    out = []
    for dog in dogs:
        try:
            dog_id = dog.find_element_by_class_name('list-animal-id').get_attribute('innerHTML')
            dog_sex_status = dog.find_element_by_class_name('list-animal-sexSN').get_attribute('innerHTML')
            dog_breed = dog.find_element_by_class_name('list-animal-breed').get_attribute('innerHTML')
            dog_age = dog.find_element_by_class_name('list-animal-age').get_attribute('innerHTML')
            dog_url = f'https://ws.petango.com/webservices/adoptablesearch/wsAdoptableAnimalDetails.aspx?id={dog_id}&css=http://ws.petango.com/WebServices/adoptablesearch/css/styles.css'
            out.append([dog_id, dog_sex_status, dog_breed, dog_age, dog_url])
        except:
            pass

    # put it in a df for processing, then filter out existing dogs
    df = pd.DataFrame(out, columns=['dog_id', 'sex', 'breed', 'age', 'link'])
    existing_dogs = pd.read_csv('existing_dogs.csv')
    new_dogs = df[~df.dog_id.astype(int).isin(existing_dogs['dog_id'])]
    df['dog_id'].to_csv('existing_dogs.csv', index=False)

    # if no new dogs, quit
    if len(new_dogs.index) == 0:
        print('No new dogs to report :(')
    else:

        # if new dogs, write an email
        try:
            # Create a secure SSL context
            context = ssl.create_default_context()
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Dog adoption update: {len(new_dogs.index)} new dogs listed"
            message["From"] = u
            message["To"] = ", ".join(recipients)
            html = f"""\
            <html>
              <body>
                {new_dogs.to_html()}
              </body>
            </html>
            """
            part2 = MIMEText(html, "html")
            message.attach(part2)

        #     attachement
        #     filename = f'{Group.id}/hourly_summary_{Group.id}.xlsx'
        #     part = MIMEBase('application', "octet-stream")
        #     part.set_payload(open(filename, "rb").read())
        #     encoders.encode_base64(part)
        #     part.add_header('Content-Disposition',
        #                     f'attachment; filename="{filename}"')
        #     message.attach(part)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(u, p)
                server.sendmail(u, recipients, message.as_string())

        except Exception as e:
            print(f'Something went wrong... | {e}')

# dog_scrape()
