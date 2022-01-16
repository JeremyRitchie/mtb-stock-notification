from selenium import webdriver
import json
import boto3

def lambda_handler(event=None, context=None):
    options = webdriver.ChromeOptions()
    options.binary_location = "/opt/bin/headless-chromium"
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")

    options.add_argument("--disable-crash-reporter");
    options.add_argument("--disable-extensions");
    options.add_argument("--disable-in-process-stack-traces");
    options.add_argument("--disable-logging");
    options.add_argument("--disable-dev-shm-usage");
    options.add_argument("--log-level=3");
    options.add_argument("--output=/dev/null");

    options.page_load_strategy = 'eager'


    driver = webdriver.Chrome("/opt/bin/chromedriver",
                              options=options)

    sns_client = boto3.client('sns')


    bikes = [
    'https://www.wiggle.co.nz/nukeproof-mega-290-factory-carbon-bike-xt-2021',
    'https://www.wiggle.co.nz/nukeproof-mega-275-factory-carbon-bike-xt-2021',
    'https://www.wiggle.co.nz/nukeproof-giga-275-factory-carbon-bike-xt-2021',
    'https://www.wiggle.co.nz/nukeproof-giga-290-factory-carbon-bike-xt-2021',
    'https://www.wiggle.co.nz/nukeproof-mega-297-mx-bike-xo1-2022'
    ]

    for bike in bikes:
        try:
            driver.get(bike)
            for bike_driver in driver.find_elements_by_class_name("bem-sku-selector__option-group-item"):
                size = bike_driver.get_attribute("title").lower()
                status = json.loads(bike_driver.find_element_by_xpath("input").get_attribute("data-display-buy"))['ProductAvailabilityMessage'].lower()
                if size == 'large':
                    if 'currently out of stock' not in status:
                        print(f"{bike.split('/')[-1].replace('-',' ')} available in {size}. See here - {bike}")
                        sns_client.publish(TopicArn='arn:aws:sns:ap-southeast-2:747340109238:mobile', Message=f"{bike.split('/')[-1].replace('-',' ')} available in {size}. See here - {bike}")
                    else:
                        print(f"{bike.split('/')[-1].replace('-',' ')} is unavailable in {size}")
        except Exception as e:
            sns_client.publish(TopicArn='arn:aws:sns:ap-southeast-2:747340109238:personal-email', Message=f"MTB Lambda Error: {e}")
            print(e)

    driver.quit()

    return {
        'statusCode': 200,
        'body': 'success'
    }

lambda_handler()