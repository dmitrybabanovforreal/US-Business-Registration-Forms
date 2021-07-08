import logging, datetime, traceback, os, time, sys, random, bs4, json, csv, imaplib, email
from difflib import SequenceMatcher
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as WDW
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_element_located as pres
from selenium.webdriver.support.expected_conditions import visibility_of_element_located as visible
from selenium.webdriver.support.expected_conditions import element_to_be_clickable as clickable
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


def random_string_generator(str_size):
    allowed_chars = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(random.choice(allowed_chars) for x in range(str_size))


def click_and_compare(handle_type, handle):
    i = 0
    while i < 10:
        i += 1
        if handle_type == 'selector':
            elem = WDW(browser, 10).until(pres((By.CSS_SELECTOR, handle)))
        elif handle_type == 'xpath':
            elem = WDW(browser, 10).until(pres((By.XPATH, handle)))
        elif handle_type == 'partial text':
            elem = WDW(browser, 10).until(pres((By.PARTIAL_LINK_TEXT, handle)))
        time.sleep(1)
        before = browser.page_source
        try:
            elem.click()
        except (StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException):
            pass
        time.sleep(1)
        after = browser.page_source
        if before != after:
            return None
    raise Exception('Could not click the element')


def mississippi_dropdown(handle_type, handle, text):
    if handle_type == 'selector':
        elem = WDW(browser, 10).until(pres((By.CSS_SELECTOR, handle)))
    elif handle_type == 'xpath':
        elem = WDW(browser, 10).until(pres((By.XPATH, handle)))
    elif handle_type == 'partial text':
        elem = WDW(browser, 10).until(pres((By.PARTIAL_LINK_TEXT, handle)))
    elem.clear()
    elem.send_keys(text)
    time.sleep(0.5)
    elem.send_keys(Keys.ENTER)
    time.sleep(0.5)


def tennessee_field_fill(data, rediscover):
    # data is a dictionary, each items is [fieldType, fieldName, fieldValue]
    # fieldType can be radio, select, text
    # rediscover parameter determines whether the funcion need to search for elems every time after filling another field (for the forms with dynamic filed enabling)
    searchElems = True
    for item in data:
        i = 0
        while True:
            i += 1
            try:
                time.sleep(0.5)

                if searchElems:
                    radioFields = browser.find_elements_by_xpath('//div[starts-with(@class, "FGFC") and contains(@class, "FGControlComboboxButton") and not(contains(@class, "Hidden"))]')
                    selectFields = browser.find_elements_by_xpath('//div[contains(@class, "FGControlCombobox FieldEnabled")]')
                    textFields = browser.find_elements_by_xpath('//div[contains(@class, "FGControlMask Field") or contains(@class, "FGControlText FieldEnabled") or contains(@class, "FGControlEmail FieldEnabled") or contains(@class, "FGControlDate FieldEnabled")]')
                    if not rediscover:
                        searchElems = False

                fieldType = item[0]
                fieldName = item[1]
                fieldValue = item[2]
                elem = None
                if fieldType == 'radio':
                    for x in radioFields:
                        if fieldName in x.text:
                            elem = x
                            break
                    if fieldValue:
                        elem.find_elements_by_tag_name('label')[1].click()
                    else:
                        elem.find_elements_by_tag_name('label')[2].click()
                elif fieldType == 'text':
                    for x in textFields:
                        if fieldName in x.text:
                            elem = x
                            break
                    elem.find_element_by_tag_name('input').send_keys(fieldValue)
                elif fieldType == 'select':
                    for x in selectFields:
                        if fieldName in x.text:
                            elem = x
                            break
                    selectElem = elem.find_element_by_tag_name('select')
                    Select(selectElem).select_by_value(fieldValue)
                else:
                    raise Exception('could not find the field ' + fieldName)
                break
            except AttributeError:
                if i == 3:
                    raise Exception('Could not fill the field ' + fieldName)
                time.sleep(0.5)


def button_click(name):
    i = 0
    while i < 7:
        i += 1
        try:
            for elem in browser.find_elements_by_tag_name('button'):
                if elem.text.strip().lower() == name.strip().lower():
                    button = elem
            button.click()
            time.sleep(1)
            return None
        except (StaleElementReferenceException, ElementClickInterceptedException):
            time.sleep(1)


def california_field_fill(data, rediscover):
    # data is a dictionary, each items is [fieldType, fieldName, fieldValue]
    # fieldType can be radio, select, text, checkbox

    # rediscover parameter determines whether the funcion need to search for elems every time after filling another field (for the forms with dynamic filed enabling)

    searchElems = True
    for item in data:
        i = 0
        while True:
            i += 1
            try:
                if searchElems:
                    elems = []
                    for elem in browser.find_elements_by_xpath('//tr[starts-with(@id, "container_")]') + browser.find_elements_by_xpath('//div[starts-with(@id, "container_")]'):
                        elems.append([elem.text, elem])
                    if not rediscover:
                        searchElems = False

                fieldType = item[0]
                fieldName = item[1]
                fieldValue = item[2]
                elem = None
                if fieldType == 'checkbox':
                    for x in elems:
                        if fieldName in x[0]:
                            elem = x[1]
                            if x[0].startswith(fieldName):
                                break
                    elem.find_element_by_tag_name('input').click()
                elif fieldType == 'radio':
                    for x in elems:
                        if fieldName in x[0]:
                            elem = x[1]
                            if x[0].startswith(fieldName):
                                break
                    if fieldValue:
                        radioButton = elem.find_elements_by_tag_name('label')[1]
                    else:
                        radioButton = elem.find_elements_by_tag_name('label')[2]
                    try:
                        radioButton.click()
                    except ElementClickInterceptedException:
                        radioButton.find_element_by_tag_name('span').click()
                elif fieldType == 'text':
                    for x in elems:
                        text = x[0]
                        if fieldName in text:
                            elem = x[1]
                            if text.startswith(fieldName):
                                break
                    elem.find_element_by_tag_name('input').send_keys(fieldValue)
                elif fieldType == 'textLatest':
                    for x in elems:
                        text = x[0]
                        if fieldName in text and text.startswith(fieldName):
                            elem = x[1]
                    elem.find_element_by_tag_name('input').send_keys(fieldValue)
                elif fieldType == 'textarea':
                    for x in elems:
                        text = x[0]
                        if fieldName in text:
                            elem = x[1]
                            if text.startswith(fieldName):
                                break
                    elem.find_element_by_tag_name('textarea').send_keys(fieldValue)
                elif fieldType == 'select':
                    for x in elems:
                        if fieldName in x[0]:
                            elem = x[1]
                            break
                    selectElem = elem.find_element_by_tag_name('select')
                    Select(selectElem).select_by_visible_text(fieldValue)
                elif fieldType == 'selectValue':
                    for x in elems:
                        if x[0].startswith(fieldName):
                            elem = x[1]
                            break
                    selectElem = elem.find_element_by_tag_name('select')
                    Select(selectElem).select_by_value(fieldValue)
                break
            except (AttributeError, StaleElementReferenceException):
                time.sleep(1)
                if i == 3:
                    raise Exception('Could not find the field ' + fieldName)


def massachusetts_field_fill(data, rediscover):
    # data is a dictionary, each items is [fieldType, fieldName, fieldValue]
    # fieldType can be radio, select, text
    # rediscover parameter determines whether the funcion need to search for elems every time after filling another field (for the forms with dynamic filed enabling)
    searchElems = True
    for item in data:
        i = 0
        while True:
            i += 1
            try:
                if searchElems:
                    radioFields = browser.find_elements_by_xpath('//div[starts-with(@class, "FGFC") and contains(@class, "FGControlComboboxButton") and not(contains(@class, "Hidden"))]')
                    selectFields = browser.find_elements_by_xpath('//div[contains(@class, "FGControlCombobox FieldEnabled")]')
                    textFields = browser.find_elements_by_xpath('//div[contains(@class, "FGControlMask Field") or contains(@class, "FGControlText FieldEnabled") or contains(@class, "FGControlEmail FieldEnabled") or contains(@class, "FGControlDate FieldEnabled")]')
                    checkboxFields = browser.find_elements_by_xpath('//div[contains(@class, "FGControlCheckbox FieldEnabled")]')
                    if not rediscover:
                        searchElems = False

                fieldType = item[0]
                fieldName = item[1]
                fieldValue = item[2]
                elem = None
                if fieldType == 'radio':
                    time.sleep(0.3)
                    for x in radioFields:
                        if fieldName in x.text:
                            elem = x
                            break
                    if fieldValue:
                        elem.find_elements_by_tag_name('label')[1].click()
                    else:
                        elem.find_elements_by_tag_name('label')[2].click()
                elif fieldType == 'checkbox':
                    for x in checkboxFields:
                        if fieldName in x.text:
                            elem = x
                            break
                    elem.find_element_by_tag_name('input').click()
                elif fieldType == 'text':
                    for x in textFields:
                        if fieldName in x.text:
                            elem = x
                            break
                    elem.find_element_by_tag_name('input').send_keys(fieldValue)
                elif fieldType == 'select':
                    for x in selectFields:
                        if fieldName in x.text:
                            elem = x
                            break
                    selectElem = elem.find_element_by_tag_name('select')
                    selectElem.click()
                    Select(selectElem).select_by_value(fieldValue)
                else:
                    raise Exception('could not find the field ' + fieldName)
                break
            except ElementClickInterceptedException:
                browser.find_element_by_tag_name('html').send_keys(Keys.PAGE_DOWN)
                searchElems = True
            except (AttributeError, StaleElementReferenceException, NoSuchElementException):
                if i == 10:
                    raise Exception('Could not fill the field ' + fieldName)
                time.sleep(1)
                searchElems = True


def massachusetts_button_click(selector):
    i = 0
    time.sleep(0.5)
    text1 = browser.find_element_by_tag_name('html').text
    while i < 7:
        try:
            i += 1
            WDW(browser, 10).until(pres((By.CSS_SELECTOR, selector))).click()
            time.sleep(1)
            text2 = browser.find_element_by_tag_name('html').text
            if text1 != text2:
                return None
        except (StaleElementReferenceException, ElementClickInterceptedException):
            text2 = browser.find_element_by_tag_name('html').text
            if text1 != text2:
                return None


def missouri_radio_click(text, answer):
    questionBlock = None
    for elem in browser.find_elements_by_xpath('//div[@class="form-group"]'):
        if text in elem.text:
            questionBlock = elem
            break
    if questionBlock is None:
        raise Exception('could not find the element containing the text: ' + text)
    html = questionBlock.get_property('outerHTML')
    soup = bs4.BeautifulSoup(html, 'html.parser')
    elemId = soup.find_all(attrs={"value" : answer})[0]['id']
    elem = questionBlock.find_element_by_id(elemId)
    elem.send_keys(Keys.SPACE)


def select_the_best_match(xpath, text):
    i = 0
    while True:
        options = Select(WDW(browser, 10).until(pres((By.XPATH, xpath)))).options
        if len(options) > 1:
            break
        time.sleep(1)
        i += 1
        if i == 10:
            raise Exception('no options available to choose from')
    bestMatchRatio = 0
    for option in options:
        matchRatio = SequenceMatcher(None, option.text.lower(), text.lower()).ratio()
        if matchRatio > bestMatchRatio:
            bestMatchRatio = matchRatio
            bestMatch = option
    Select(WDW(browser, 10).until(pres((By.XPATH, xpath)))).select_by_visible_text(bestMatch.text)


def missouri_save_address():
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#nextTaxFormBtn'))).click()
    i = 0
    while True:
        time.sleep(2)
        i += 1
        if 'The address has been corrected to match mailing standards' in browser.find_element_by_tag_name('html').text:
            WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#okBtn'))).click()
            break
        if 'Do you make retail sales in this state' in browser.find_element_by_tag_name('html').text:
            break
        if i == 15:
            raise Exception('could not jump to the next page')


def select_the_best_match_radio(xpath, text, optionsText):
    i = 0
    while True:
        options = browser.find_elements_by_xpath(xpath)
        if len(options) > 1:
            break
        time.sleep(1)
        i += 1
        if i == 10:
            raise Exception('no options available to choose from')
    bestMatchRatio = 0
    optionsTexts = optionsText.strip().split('\n')
    if len(optionsTexts) != len(options):
        raise Exception('could not find the correct options texts')
    for i, option in enumerate(optionsTexts):
        matchRatio = SequenceMatcher(None, option.lower(), text.lower()).ratio()
        if matchRatio > bestMatchRatio:
            bestMatchRatio = matchRatio
            bestMatch = option
            bestMatchInd = i
    options[bestMatchInd].click()


def record_the_output(text):
    outputFileName = f'{business["name"]} registration {appLaunchTimeSpamp}.txt'
    outputFile = open(os.path.join(user_path, outputFileName), 'a')
    outputFile.write(text + '\n')
    outputFile.close()


def get_the_confirmation_email(subjectLine):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(emailAccount, emailPassword)
    mail.select('inbox')

    confirmationMsg = None
    while True:
        data = mail.search(None, 'ALL')
        mail_ids = data[1]
        id_list = mail_ids[0].split()
        first_email_id = int(id_list[-30])
        latest_email_id = int(id_list[-1])

        for emailId in range(latest_email_id, first_email_id, -1):
            data = mail.fetch(str(emailId), '(RFC822)')
            for response_part in data:
                arr = response_part[0]
                if isinstance(arr, tuple):
                    msg = email.message_from_string(str(arr[1], 'utf-8'))
                    subject = msg['subject']
            if subject.strip() == subjectLine:
                confirmationMsg = msg
                break
        if confirmationMsg is None:
            time.sleep(5)
        else:
            break

    for part in confirmationMsg.walk():
        if part.get_content_type() == "text/plain":  # ignore attachments/html
            body = str(part.get_payload(decode=True))

    return body


# todo complete the Missouri and Kansas parts:
def missouri():
    browser.get('https://mytax.mo.gov/rptp/portal/business/register-new-business/')
    elem = WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#termsChkBox')))
    elem.send_keys(Keys.END)
    time.sleep(0.5)
    elem.send_keys(Keys.SPACE)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#termsNextBtn'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#firstName'))).send_keys(business['officer']['first name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#lastName'))).send_keys(business['officer']['last name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#dayPhone'))).send_keys(business['officer']['phone'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#email'))).send_keys(business['officer']['email'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#confirmEmail'))).send_keys(business['officer']['email'])
    browser.find_element_by_tag_name('html').send_keys(Keys.PAGE_DOWN)

    # todo Rearrange the flow so that all manual stuff is done in the beginning
    # wait till the user passes the reCAPTCHA and goes to the next page
    while 'What is your business ownership type?' not in browser.find_element_by_tag_name('html').text:
        time.sleep(2)

    if business['type'] == 'Sole Proprietorship':
        Select(WDW(browser, 10).until(pres((By.XPATH, '//select[contains(@id, "OwnershipType")]')))).select_by_visible_text('SOLE PROPRIETOR')
    else:
        Select(WDW(browser, 10).until(pres((By.XPATH, '//select[contains(@id, "OwnershipType")]')))).select_by_visible_text('LLC CORPORATION')
    WDW(browser, 10).until(pres((By.XPATH, '//input[contains(@id, "FirstName")]'))).send_keys(business['officer']['first name'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[contains(@id, "LastName")]'))).send_keys(business['officer']['last name'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[contains(@id, "MailAddr_X_addrl1")]'))).send_keys(business['address']['street1'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[contains(@id, "MailAddr_X_addrl2")]'))).send_keys(business['address']['street2'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[contains(@id, "MailAddr_X_city")]'))).send_keys(business['address']['city'])
    Select(WDW(browser, 10).until(pres((By.XPATH, '//select[contains(@id, "MailAddr_X_state")]')))).select_by_value(business['address']['state'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[contains(@id, "MailAddr_X_zip")]'))).send_keys(business['address']['zip'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[contains(@id, "Phone_phoneNonIntl")]'))).send_keys(business['officer']['phone'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[contains(@id, "Email") and not(contains(@id, "EmailCheck"))]'))).send_keys(business['officer']['email'])
    missouri_radio_click('Is your record storage address the same as above', 'yes')
    WDW(browser, 10).until(pres((By.XPATH, '//input[contains(@id, "StartDate")]'))).send_keys(business['business commenced'].strftime('%m/%d/%Y'))
    missouri_save_address()

    missouri_radio_click('Do you make retail sales in this state to other customers of this state', 'yes')
    missouri_radio_click('Are you an out-of-state business that plans to make retail sales to Missouri customers', 'yes')
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#nextTaxFormBtn'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#nextTaxFormBtn'))).click()

    WDW(browser, 10).until(pres((By.XPATH, '//input[contains(@id, "FEIN")]'))).send_keys(business['FEIN'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[contains(@id, "SSN")]'))).send_keys(business['officer']['SSN'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[contains(@id, "OwnerDOB")]'))).send_keys(business['officer']['birth date'].strftime('%m/%d/%Y'))
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#nextTaxFormBtn'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#nextRepeatingSummaryBtn'))).click()

    WDW(browser, 10).until(pres((By.XPATH, '//select[contains(@id, "FormAddr")]'))).send_keys(business['address']['street1'][0])
    WDW(browser, 10).until(pres((By.XPATH, '//input[contains(@id, "SalesBeginDate")]'))).send_keys(business['business commenced'].strftime('%m/%d/%Y'))
    WDW(browser, 10).until(pres((By.XPATH, '//input[contains(@id, "FormsPhone_phoneNonIntl")]'))).send_keys(business['officer']['phone'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[contains(@id, "Email") and not(contains(@id, "EmailCheck"))]'))).send_keys(business['officer']['email'])
    Select(WDW(browser, 10).until(pres((By.XPATH, '//select[contains(@id, "FormAddr_X_state")]')))).select_by_value(business['address']['state'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[contains(@id, "EstMonthlySale")]'))).send_keys(business['projected monthly sales'])
    select_the_best_match('//select[contains(@id, "NAICS_naics_cat")]', naicsCodes[business['NAICS']]['categoryName'])
    select_the_best_match('//select[contains(@id, "NAICS_naics_sub_cat")]', naicsCodes[business['NAICS']]['subCategoryName'])
    select_the_best_match('//select[contains(@id, "NAICS_naics_code")]', naicsCodes[business['NAICS']]['name'])
    missouri_save_address()

    # todo Question 1
    # WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#addRepeatingSection'))).click()
    # WDW(browser, 10).until(pres((By.XPATH, '//input[contains(@id, "DBAName")]'))).send_keys(business['name'])
    # WDW(browser, 10).until(pres((By.XPATH, '//select[contains(@id, "LocAddr")]'))).send_keys(business['address']['street1'][0])
    # WDW(browser, 10).until(pres((By.XPATH, '//input[contains(@id, "LocPhone_phoneNonIntl")]'))).send_keys(business['officer']['phone'])
    # WDW(browser, 10).until(pres((By.XPATH, '//input[contains(@id, "LocEmail") and not(contains(@id, "EmailCheck"))]'))).send_keys(business['officer']['email'])
    # Select(WDW(browser, 10).until(pres((By.XPATH, '//select[contains(@id, "LocAddr_X_state")]')))).select_by_value(business['address']['state'])
    # missouri_save_address()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#nextRepeatingSummaryBtn'))).click()


def kansas():
    browser.get('https://www.kdor.ks.gov/Apps/kcsc/Registration.aspx?ReturnURL=/apps/kcsc/secure/default.aspx')
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtBusName'))).send_keys(business['name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtContact'))).send_keys(business['officer']['first name'] + ' ' + business['officer']['last name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtPhone'))).send_keys(business['officer']['phone'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtEmail'))).send_keys(addressForConfirmationEmails)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtEmail2'))).send_keys(addressForConfirmationEmails)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtPassword'))).send_keys(password)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtPassword2'))).send_keys(password)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtSecAns'))).send_keys(hintAnswer)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtSecAns2'))).send_keys(hintAnswer)

    # todo Stop execution of this function here to let the user pass the captcha and click "Register". Continue after
    #  the confirmation email is received

    # get the confirmation link from the email
    emailText = get_the_confirmation_email('Ks Customer Service Center Email Verification.')
    confirmationLink = 'https://www.kdor.ks.gov/Apps/kcsc/Login.aspx?v=' \
                       + emailText.split('https://www.kdor.ks.gov/Apps/kcsc/Login.aspx?v=')[1].split(' ')[0]
    browser.get(confirmationLink)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtUserName'))).send_keys(addressForConfirmationEmails)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtPassword'))).send_keys(password)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_cmdSignIn'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_btnEmailVerifyContinue'))).click()
    WDW(browser, 10).until(pres((By.LINK_TEXT, 'here'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_pBtrNew > a'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_rblReason_for_Application_0'))).click()
    # todo Question 2
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_ckbTaxType_0'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_ckbTaxType_1'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_btnSubmit'))).click()

    if business['type'] == 'Sole Proprietorship':
        WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_rblOwnerShip_0'))).click()
    else:
        WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_rblOwnerShip_4'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtBusinessEntity_Name'))).send_keys(business['name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtBusinessTaxpayer_ID'))).send_keys(business['FEIN'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtBusinessEntity_Phone'))).send_keys(business['officer']['phone'])
    Select(WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_ddlContactPhoneType')))).select_by_value('B')
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtBusinessAddress1'))).send_keys(business['address']['street1'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtBusinessAddress2'))).send_keys(business['address']['street2'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtBusinessCity'))).send_keys(business['address']['city'])
    Select(WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_ucStateKs_ddlState')))).select_by_value(business['address']['state'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtBusinessZip'))).send_keys(business['address']['zip'])
    # todo Question 3. Select "1" in the next line if Accrual basis
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_rbltAccount_Method_0'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtNAICS'))).send_keys(business['NAICS'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_btnSubmit'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_hlnkPreviousAdd'))).click()

    # todo Question 4

    time.sleep(0.5)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_hlnkPreviousContinue'))).click()
    time.sleep(0.5)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_hlnkCurrentContinue'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtDBA_Name'))).send_keys(business['name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtLoc_Phone'))).send_keys(business['officer']['phone'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtLocAddress1'))).send_keys(business['address']['street1'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtLocAddress2'))).send_keys(business['address']['street2'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtLocCity'))).send_keys(business['address']['city'])
    Select(WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_ucStateKsucTradeBusinessState_ddlState')))).select_by_value(business['address']['state'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtLocZip'))).send_keys(business['address']['zip'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtNAICS'))).send_keys(business['NAICS'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_btnSubmit'))).click()
    time.sleep(1)
    if 'Date retail sales/compensating use began in Kansas' not in browser.find_element_by_tag_name('html').text:
        WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtLoc_Phone'))).send_keys(business['officer']['phone'])
        WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_btnSubmit'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtUnder_This_Ownership_Dt'))).send_keys(business['business commenced'].strftime('%m/%d/%Y'))
    # todo Question 5
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_rblFilingForAll_Locations_IND_0'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_ddlSalesFrom_Temporary_Location_IND_1'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_rblDelivered_IND_0'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_rblPurchase_Home_Use_IND_1'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_rblSeasonal_1'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_rblAnnualSales_1'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_rblInternetSales_IND_0'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_rblSalesmanOnly_IND_0'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_rbUtility_IND_1'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_btnSubmit'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_hlnkContinue',))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_hlnkContinue'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtFirstName'))).send_keys(business['officer']['first name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtLastName'))).send_keys(business['officer']['last name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_rblPowerOfAttorney_1'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_rblProofOfExecutor_1'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtTaxpayer_ID'))).send_keys(business['officer']['SSN'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtOwnerPhone'))).send_keys(business['officer']['phone'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtAddress1'))).send_keys(business['officer']['address']['street1'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtAddress2'))).send_keys(business['officer']['address']['street2'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtCity'))).send_keys(business['officer']['address']['city'])
    Select(WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_ucStateKs_ddlState')))).select_by_value(business['officer']['address']['state'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtZip'))).send_keys(business['officer']['address']['zip'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtOwnership_Dt'))).send_keys(business['officer']['commence'].strftime('%m/%d/%Y'))
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_ddlFund_Control_IND_0'))).click()
    if not WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtTaxpayer_ID'))).get_property('value'):
        WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_txtTaxpayer_ID'))).send_keys(business['officer']['SSN'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_btnSubmit'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_hlnkContinue',))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cphBody_btnSubmit'))).click()

    text = browser.find_element_by_tag_name('html').text
    confirmationCode = text.split('Confirmation Number Is :')[1].split('\n')[0].strip()

    record_the_output('Kansas email used for account registration: ' + addressForConfirmationEmails)
    record_the_output('Kansas confirmation code: ' + confirmationCode)


def district_of_columbia():
    browser.get('https://mytax.dc.gov/_/#1')

    # the first page
    WDW(browser, 10).until(pres((By.LINK_TEXT, 'Register a New Business - Form FR-500'))).click()
    click_and_compare('selector', '#action_5')  # click Next
    if business['type'] == 'Sole Proprietorship':
        Select(WDW(browser, 10).until(pres((By.XPATH, '//select[@id="Dp-d"]')))).select_by_visible_text('Sole Proprietor')
    else:
        Select(WDW(browser, 10).until(pres((By.XPATH, '//select[@id="Dp-d"]')))).select_by_visible_text('Limited Liability Company')
    WDW(browser, 5).until(pres((By.XPATH, '//label[@class="FastComboButtonItem FastComboButtonItem_FEIN FastComboButton FRC"]')))  # select FEIN
    while 'Federal Employer Id' not in browser.page_source:
        time.sleep(2)
        browser.find_element_by_xpath('//label[@class="FastComboButtonItem FastComboButtonItem_FEIN FastComboButton FRC"]').click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp-g'))).send_keys(business['FEIN'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp-h'))).send_keys(business['FEIN'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp-i'))).send_keys(business['name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp-x'))).send_keys(business['address']['street1'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp-y'))).send_keys(business['address']['street2'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp-11'))).send_keys(business['address']['city'])
    Select(WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp-21')))).select_by_value(business['address']['state'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp-31'))).send_keys(business['address']['zip'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp-61'))).click()  # verify address

    # If verification goes wrong way:
    time.sleep(2)
    if 'No valid address was found.  Please verify input and revalidate.' in browser.page_source:
        raise Exception('Address not found for ' + str(business['address']))
    elif 'Select this address' in browser.page_source:
        click_and_compare('partial text', 'As Entered')
        # confirm selecting unverified address:
        click_and_compare('selector', 'body > div.ui-dialog.ui-corner-all.ui-widget.ui-widget-content.ui-front.FastMessageBox.FastPanelDialog.FastModal.MC_Default.BlankTitle.ui-dialog-modal.ui-dialog-buttons.ui-draggable.fast-ui-dialog-positioned.fast-ui-dialog-open > div.ui-dialog-buttonpane.ui-widget-content.ui-helper-clearfix > div > button.FastMessageBoxButtonYes.ui-button.ui-corner-all.ui-widget')

    click_and_compare('selector', '#action_5')  # click Next

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp-r1'))).send_keys(business['business commenced'].strftime('%d-%b-%Y'))
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dr-3'))).send_keys(Keys.PAGE_DOWN)
    ActionChains(browser).move_to_element(WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dr-3')))).perform()
    # click Lookup NAICS and fill the popup window
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dr-3'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dc_1-8'))).send_keys(business['NAICS'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dc_1-9'))).click()
    WDW(browser, 10).until(pres((By.LINK_TEXT, business['NAICS']))).click()
    click_and_compare('selector', '#action_1')
    # click New Officer and fill the popup window
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Ds-4'))).click()
    WDW(browser, 10).until(pres((By.LINK_TEXT, 'Add a Record'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Ds_1-o-1'))).clear()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Ds_1-o-1'))).send_keys(business['officer']['commence'].strftime('%d-%b-%Y'))
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Ds_1-p-1'))).send_keys(business['officer']['cease'].strftime('%d-%b-%Y'))
    Select(WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Ds_1-q-1')))).select_by_visible_text('Owner')
    Select(WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Ds_1-r-1')))).select_by_visible_text('SSN')
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Ds_1-s-1'))).send_keys(business['officer']['SSN'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Ds_1-t-1'))).send_keys(business['officer']['first name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Ds_1-v-1'))).send_keys(business['officer']['last name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Ds_1-w-1'))).send_keys(business['officer']['email'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Ds_1-x-1'))).send_keys(business['officer']['phone'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Ds_1-z-1'))).send_keys(business['officer']['address']['street1'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Ds_1-01-1'))).send_keys(business['officer']['address']['street2'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Ds_1-31-1'))).send_keys(business['officer']['address']['city'])
    Select(WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Ds_1-41-1')))).select_by_value(business['officer']['address']['state'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Ds_1-51-1'))).send_keys(business['officer']['address']['zip'])
    click_and_compare('selector', '#Ds_1-d > div > button.ActionButton.ActionButtonOK.FastEvt')  # press OK to close the popup window
    click_and_compare('selector', '#action_5')  # click Next

    # select Yes for Sales and Use Tax and go the the next page
    while True:
        try:
            time.sleep(0.5)
            ActionChains(browser).move_to_element(WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp-u2')))).perform()
            time.sleep(0.5)
            WDW(browser, 10).until(clickable((By.TAG_NAME, 'html'))).send_keys(Keys.ARROW_DOWN, Keys.ARROW_DOWN, Keys.ARROW_DOWN, Keys.ARROW_DOWN)
            time.sleep(0.5)
            WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp-u2 > div > label.FastComboButtonItem.FastComboButtonItem_Yes.FastComboButton.FRC'))).click()
            time.sleep(0.5)
            break
        except:
            continue
    click_and_compare('selector', '#action_5')  # click Next

    click_and_compare('selector', '#action_5')  # click Next

    # Add location that collects Sales and Use Tax
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp-s6'))).click()  # Add location
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp_1-37 > tbody > tr > td > a'))).click()  # Add a record


    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp_1-l7-1 > div > label.FastComboButtonItem.FastComboButtonItem_No.FastComboButton.FRC'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp_1-m7-1 > div > label.FastComboButtonItem.FastComboButtonItem_Yes.FastComboButton.FRC'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp_1-q7-1 > div > label.FastComboButtonItem.FastComboButtonItem_No.FastComboButton.FRC'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp_1-s7-1 > div > label.FastComboButtonItem.FastComboButtonItem_Yes.FastComboButton.FRC'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp_1-t7-1 > div > label.FastComboButtonItem.FastComboButtonItem_No.FastComboButton.FRC'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp_1-y7-1'))).send_keys(business['officer']['address']['street1'])  # Location Doing Business As (DBA) / Trade Name
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp_1-z7-1'))).send_keys(business['officer']['phone'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp_1-18-1'))).send_keys(business['officer']['address']['street1'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp_1-28-1'))).send_keys(business['officer']['address']['street2'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp_1-78-1'))).send_keys(business['officer']['address']['zip'])
    Select(WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp_1-68-1')))).select_by_value(business['officer']['address']['state'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp_1-58-1'))).send_keys(business['officer']['address']['city'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp_1-98-1'))).click()  # verify address

    # If verification goes wrong way:
    time.sleep(2)
    if 'No valid address was found.  Please verify input and revalidate.' in browser.page_source:
        raise Exception('Address not found for ' + str(business['address']))
    elif 'Select this address' in browser.page_source:
        click_and_compare('partial text', 'As Entered')
        # confirm selecting unverified address:
        click_and_compare('selector', 'body > div.ui-dialog.ui-corner-all.ui-widget.ui-widget-content.ui-front.FastMessageBox.FastPanelDialog.FastModal.MC_Default.BlankTitle.ui-dialog-modal.ui-dialog-buttons.ui-draggable.fast-ui-dialog-positioned.fast-ui-dialog-open > div.ui-dialog-buttonpane.ui-widget-content.ui-helper-clearfix > div > button.FastMessageBoxButtonYes.ui-button.ui-corner-all.ui-widget')

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Dp_1-47 > div > button.ActionButton.ActionButtonOK.FastEvt'))).click()
    click_and_compare('selector', '#action_5')  # click Next

    click_and_compare('selector', '#action_7')  # click Submit
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#CONFIRMATION_EMAIL1__'))).send_keys(business['officer']['email'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#CONFIRMATION_EMAIL2__'))).send_keys(business['officer']['email'])
    click_and_compare('selector', '#ConfirmationForm > div.ActionBar.ModalActionBar > button.ActionButton.ActionButtonOK.FastEvt')

    time.sleep(2)
    text = WDW(browser, 10).until(pres((By.TAG_NAME, 'p'))).text
    confirmationCode = text.split('Confirmation Code:')[1].split('\n')[0].strip()
    record_the_output('District of Columbia confirmation code: ' + confirmationCode)


def mississippi():
    browser.get('https://tap.dor.ms.gov/_/#1')
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cl_d-11'))).click()  # register new business
    click_and_compare('selector', '#d-42')  # new taxpayer
    # Step 1. Taxpayer information
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cl_g-8'))).click()
    mississippi_dropdown('selector', '#g-01s2', 'LLC/Single Member LLC')
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-01v2'))).send_keys(business['FEIN'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-01s2'))).click()
    time.sleep(0.3)
    mississippi_dropdown('selector', '#g-01u2', 'No')
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-01i2 > div > button.ActionButton.ActionButtonOK'))).click()
    time.sleep(2)
    if 'We have record of this ID previously having filed in the Mississippi Department of Revenue' in browser.page_source:
        raise Exception('This FEIN already registered in Mississippi')

    # Step 2. Taxpayer information
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cl_g-l'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-0104'))).send_keys(business['name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-01c4'))).send_keys(business['address']['street1'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-01h4'))).send_keys(business['address']['city'])
    mississippi_dropdown('selector', '#g-01j4', stateCodes[business['address']['state']].upper())
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-01k4'))).send_keys(business['address']['zip'])
    mississippi_dropdown('selector', '#g-01m4', business['address']['county'].upper())
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-01q4'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-01i2 > div > button.ActionButton.ActionButtonOK'))).click()
    time.sleep(2)

    # Step 3. Additional Business Information
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cl_g-91'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-01a5'))).send_keys(business['nature of business'])
    mississippi_dropdown('selector', '#g-01d5', 'LLC')
    time.sleep(0.5)
    mississippi_dropdown('selector', '#g-01g5', 'No')
    mississippi_dropdown('selector', '#g-01h5', stateCodes[business['address']['state']].upper())
    if business['type'] == 'Sole Proprietorship':
        mississippi_dropdown('selector', '#g-01m5', 'Yes')
    else:
        mississippi_dropdown('selector', '#g-01m5', 'No')
    mississippi_dropdown('selector', '#g-01v5', 'No')
    time.sleep(1)
    # Provide the information about owners
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cl_g-01y5'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-02n7 > tbody > tr > td > a'))).click()
    mississippi_dropdown('selector', '#g-02p7-1', 'Social Security')
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-02r7-1'))).send_keys(business['officer']['SSN'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-02t7-1'))).send_keys(business['officer']['first name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-02v7-1'))).send_keys(business['officer']['last name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-02y7-1'))).send_keys(business['officer']['address']['street1'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-02z7-1'))).send_keys(business['officer']['address']['city'])
    mississippi_dropdown('selector', '#g-0208-1', stateCodes[business['address']['state']].upper())
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-0218-1'))).send_keys(business['officer']['address']['zip'])
    mississippi_dropdown('selector', '#g-0228-1', 'Owner')
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-0238-1'))).send_keys('100')
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-02i2 > div > button.ActionButton.ActionButtonOK'))).click()
    time.sleep(1)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-01i2 > div > button.ActionButton.ActionButtonOK'))).click()
    time.sleep(2)

    # Attach a copy of the IRS Notice Letter CP 575
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#caption2_g-b1'))).click()
    Select(WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#AttachmentType')))).select_by_value('IRSCP')
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#AttachmentDescription'))).send_keys('EIN')
    attachmentPath = ''
    for fileName in os.listdir(os.path.join(user_path, 'Mississippi - IRS Notice Letter CP 575')):
        if fileName.lower().endswith('.pdf'):
            attachmentPath = os.path.join(user_path, 'Mississippi - IRS Notice Letter CP 575', fileName)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#AttachmentFile'))).send_keys(attachmentPath)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#AttachmentForm > div > button:nth-child(1)'))).click()
    time.sleep(2)

    # Step 4: NAICS Code
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cl_g-p1'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#c-108'))).send_keys(business['NAICS'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#c-109'))).click()
    time.sleep(2)

    # Step 5: Account Access Information
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#cl_g-y1'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-01n8'))).send_keys(business['officer']['first name'] + ' ' + business['officer']['last name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-01p8'))).send_keys(business['officer']['email'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-01r8'))).send_keys(business['officer']['email'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-01x8'))).send_keys(business['officer']['phone'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-0159'))).send_keys(username)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-0189'))).send_keys(password)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-01a9'))).send_keys(password)
    mississippi_dropdown('selector', '#g-01d9', 'first pet')
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-01f9'))).send_keys(hintAnswer)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-01h9'))).send_keys(hintAnswer)
    mississippi_dropdown('selector', '#g-01n9', 'no')  # no paperless
    time.sleep(1)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#g-01i2 > div > button.ActionButton.ActionButtonOK'))).click()
    time.sleep(1)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, 'body > div.ui-dialog.ui-widget.ui-widget-content.ui-corner-all.ui-front.FastMessageBox.NonContainer.FastModal.ui-dialog-buttons.ui-draggable > div.ui-dialog-buttonpane.ui-widget-content.ui-helper-clearfix > div > button:nth-child(1)'))).click()
    time.sleep(1)

    # finally, submit the application
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#action_9')))
    browser.find_elements_by_css_selector('#action_9')[1].click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#ConfirmationForm > div > button:nth-child(1)'))).click()  # confirm
    text = WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#container_c-7'))).text
    confirmationCode = text.split('Your confirmation number is:')[1].split('.')[0].strip()
    record_the_output('Mississippi confirmation code: ' + confirmationCode)


def tennessee():
    browser.get('https://tntap.tn.gov/eservices/_/#16')
    WDW(browser, 10).until(pres((By.LINK_TEXT, 'Register a New Business'))).click()

    if business['type'] == 'Sole Proprietorship':
        entityType = 'SOL'
    else:
        entityType = 'LLC'
    tennessee_field_fill(
        [
            ['radio', 'Are you an entity from outside the United States?', True],  # this radio button has reverse Yes/No order
            ['select', 'Entity Type', entityType],
            ['select', 'ID Type', 'SSN'],
            ['text', 'SSN', business['officer']['SSN']]
        ],
        True
    )
    button_click('Next')

    tennessee_field_fill([['radio', 'Are you a manufacturer of alcoholic beverages?', False]], True)  # not a manufacturer of alcoholic beverages
    button_click('Next')

    for elem in browser.find_elements_by_xpath('//div[starts-with(@class,"FGFC FGCPTop  FastLeftToolTip  FGControlCheckbox FieldEnabled")]'):
        if elem.text.strip() == 'Sales and Use Tax':
            elem.find_element_by_tag_name('input').click()
            break
    button_click('Next')

    tennessee_field_fill(
        [
            ['radio', 'Will your gross sales exceed $4,800 per year?', True],
            ['radio', 'Are you registering as a marketplace facilitator?', False],
            ['radio', 'Are you solely a manufacturer or wholesaler?', True],
            ['radio', 'Do you have a physical presence in Tennessee', False]
        ],
        True
    )
    button_click('Next')

    tennessee_field_fill(
        [
            ['radio', 'Are you a wholesaler, distributor, or manufacturer?', True],
            ['radio', 'Will you sell beer or tobacco products to Tennessee retailers?', False],
            ['radio', 'Will you sell food, candy, or non-alcoholic beverages to Tennessee retailers that sell beer or tobacco', False]
        ],
        True
    )
    button_click('Next')

    tennessee_field_fill(
        [
            ['text', 'Street', business['address']['street1']],
            ['text', 'Street 2', business['address']['street2']],
            ['text', 'City', business['address']['city']],
            ['select', 'State', business['address']['state']],
            ['text', 'Zip', business['address']['zip']],
            ['text', 'Attention', business['officer']['first name'] + ' ' + business['officer']['last name']]
        ],
        False
    )
    button_click('Click Here To Verify Address')  # click Verify address
    i = 0
    while True:
        if 'No valid address was found' in browser.page_source:
            raise Exception('Address not found for ' + str(business['address']))
        elif 'Select this address' in browser.page_source:
            WDW(browser, 10).until(pres((By.XPATH, '//tr[@class="DataRow TDRE"]'))).click()
            break
        else:
            i += 1
            if i == 10:
                raise Exception('Could not enter address')
            time.sleep(2)
    button_click('Next')

    tennessee_field_fill([['radio', 'Same as Primary?', True]], True)
    button_click('Next')

    tennessee_field_fill(
        [
            ['text', 'First Name', business['officer']['first name']],
            ['text', 'Last Name', business['officer']['last name']],
            ['text', 'Email', business['officer']['email']],
            ['select', 'Phone Type', 'BSN'],
            ['text', 'Area Code', business['officer']['phone'][:3]],
            ['text', 'Phone Number', business['officer']['phone'][3:]]
        ],
        False
    )
    button_click('Next')

    tennessee_field_fill([['text', 'Date business began at this location', business['business commenced'].strftime('%d-%b-%Y')]], False)
    for elem in browser.find_elements_by_xpath('//div[starts-with(@class,"FGFC FGCPLeft   FGControlCheckbox FieldEnabled")]'):
        if 'Same as Primary Address?' in elem.text.strip():
            elem.find_element_by_tag_name('input').click()
        if 'Same as Location Address?' in elem.text.strip():
            elem.find_element_by_tag_name('input').click()
    for elem in browser.find_elements_by_xpath('//button[@type="button"]'):
        if 'Click Here to Lookup NAICS Code' in elem.text:
            elem.click()
            break
    time.sleep(1)
    for elem in browser.find_elements_by_xpath('//tr[starts-with(@class,"ViewFieldContainer")]'):
        if 'Keyword' in elem.text:
            elem.find_element_by_tag_name('input').send_keys(business['NAICS'][:4])
            break
    button_click('Search')
    while True:
        elems = browser.find_elements_by_link_text(business['NAICS'])
        if not elems:
            WDW(browser, 10).until(pres((By.LINK_TEXT, 'Next Page'))).click()
            time.sleep(1)
            continue
        elems[0].click()
        break
    button_click('OK')
    button_click('Next')
    button_click('Next')
    button_click('Next')
    button_click('No')

    tennessee_field_fill(
        [
            ['text', 'Name', business['officer']['first name'] + ' ' + business['officer']['last name']],
            ['text', 'Email', business['officer']['email']],
            ['text', 'Verify Email', business['officer']['email']],
            ['select', 'Phone Type', 'BSN'],
            ['text', 'Area Code', business['officer']['phone'][:3]],
            ['text', 'Phone Number', business['officer']['phone'][3:]]
        ],
        False
    )
    for elem in browser.find_elements_by_xpath('//div[contains(@class,"FGControlCheckbox FieldEnabled")]'):
        if 'I certify' in elem.text.strip():
            elem.find_element_by_tag_name('input').click()
            break
    button_click('Next')
    button_click('Submit')

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#CONFIRMATION_EMAIL1__'))).send_keys(business['officer']['email'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#CONFIRMATION_EMAIL2__'))).send_keys(business['officer']['email'])
    button_click('OK')
    i = 0
    while True:
        text = browser.find_element_by_tag_name('html').text
        if 'Your request has been submitted' in text:
            confirmationCode = text.split('confirmation code: ')[1].split('.')[0].strip()
            record_the_output('Tennessee confirmation code: ' + confirmationCode)
            break
        else:
            i += 1
            time.sleep(2)
            if i == 10:
                raise Exception('Did not receive the confirmation code')
                break


def florida():
    browser.get('https://taxapps.floridarevenue.com/taxregistration')
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnRegister'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#UserName'))).send_keys(username)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#ConfirmUserName'))).send_keys(username)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#EmailAddress'))).send_keys(addressForConfirmationEmails)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#ConfirmEmailAddress'))).send_keys(addressForConfirmationEmails)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Password'))).send_keys(password)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#ConfirmPassword'))).send_keys(password)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnSubmit'))).click()

    emailText = get_the_confirmation_email('FDOR - Tax Registration Program - Registration Confirmation')
    confirmationLink = 'http://taxapps.floridarevenue.com/TaxRegistration/Account/ConfirmEmail?' + \
                       emailText.split('http://taxapps.floridarevenue.com/TaxRegistration/Account/ConfirmEmail?')[1].split('gmail.com')[0] + 'gmail.com'

    # After following the confirmation link from the email:
    browser.get(confirmationLink)
    WDW(browser, 10).until(pres((By.LINK_TEXT, 'click here to log in.'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#UserName'))).send_keys(username)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Password'))).send_keys(password)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnLogin'))).click()

    # Start new application
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNewApplication'))).click()
    WDW(browser, 10).until(pres((By.XPATH, '//span[@title="Reason for Applying"]'))).click()
    time.sleep(1.5)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#ReasonType_listbox > li:nth-child(1)'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#NewRegistration_EffectiveDate'))).send_keys(business['business commenced'].strftime('%m/%d/%Y'))
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#LegalName'))).send_keys(business['name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#PhoneNumber_Number'))).send_keys('1', Keys.BACKSPACE, business['officer']['phone'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#IsSeasonalBusiness_False'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#PhysicalLocationAddress_Street'))).send_keys(business['address']['street1'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#PhysicalLocationAddress_Street2'))).send_keys(business['address']['street2'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#PhysicalLocationAddress_City'))).send_keys(business['address']['city'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#PhysicalLocationAddress_PostalCode'))).click()
    time.sleep(1)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#PhysicalLocationAddress_PostalCode'))).send_keys(business['address']['zip'])
    WDW(browser, 10).until(pres((By.XPATH, '//span[@title="State/Region"]'))).click()
    time.sleep(1)
    WDW(browser, 10).until(pres((By.XPATH, '//span[@title="State/Region"]'))).send_keys(stateCodes[business['address']['state']].lower()[0])
    for elem in WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#PhysicalLocationAddress_RegionCode_listbox'))).find_elements_by_tag_name('li'):
        if elem.text.strip().lower() == stateCodes[business['address']['state']].lower():
            elem.click()
            break
    time.sleep(0.3)
    if stateCodes[business['address']['state']] == 'Florida':
        WDW(browser, 10).until(pres((By.XPATH, f'//span[@title="Florida County"]'))).click()
        time.sleep(1)
        for elem in WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#PhysicalLocationAddress_CountyCode_listbox'))).find_elements_by_tag_name('li'):
            if elem.text.strip().lower() == business['address']['county'].lower():
                elem.click()
                break
        time.sleep(0.3)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#BusinessMailingAddressCareOf'))).send_keys(business['name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#buttonCopyAddress'))).click()
    time.sleep(0.5)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()
    time.sleep(2)
    if 'I confirm the address entered is correct' in browser.page_source:
        WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#PhysicalLocationAddress_ValidationOverriden'))).click()
        WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#BusinessMailingAddress_ValidationOverriden'))).click()
        WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#BusinessActivityReportingType_1'))).click()  # select NAICS code
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#BusinessActivitySearchMethodType_1'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#NaicsCode'))).click()
    time.sleep(0.5)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#NaicsCode'))).send_keys(business['NAICS'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnFindNaicsCode'))).click()
    WDW(browser, 10).until(pres((By.XPATH, '//*[@id="divKnownNaicsPanel"]/div/div[2]/div[4]/div[2]/span'))).click()
    time.sleep(0.5)

    # select the SIC (nature of business) description that matches the one from input the best
    biggestMatchRatio = 0
    for i, item in enumerate(WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#ddlSicDescriptions1_listbox'))).find_elements_by_tag_name('li')):
        html = item.get_property('outerHTML')
        text = html.split('</li>')[0].split('>')[1]
        matchRatio = SequenceMatcher(None, business['nature of business'], text).ratio()
        if matchRatio > biggestMatchRatio:
            biggestMatchRatio = matchRatio
            elem = item
            elemInd = i

    i = 0
    while True:
        try:
            elem.click()
            time.sleep(0.5)
            break
        except (StaleElementReferenceException, ElementNotInteractableException):
            browser.find_element_by_tag_name('html').send_keys(Keys.DOWN, Keys.DOWN)
            WDW(browser, 10).until(pres((By.XPATH, '//*[@id="divKnownNaicsPanel"]/div/div[2]/div[4]/div[2]/span'))).click()
            elem = WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#ddlSicDescriptions1_listbox'))).find_elements_by_tag_name('li')[elemInd]
            time.sleep(0.5)
            i += 1
        if i == 5:
            raise Exception('could not select the SIC (nature of business) description')

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnAddNaicsCode1'))).click()
    time.sleep(1)
    browser.find_elements_by_tag_name('button')[-1].click()
    time.sleep(0.5)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()


    WDW(browser, 10).until(pres((By.XPATH, '//span[@title="Select your form of business ownership"]'))).click()
    time.sleep(1)
    if business['type'] == 'Sole Proprietorship':
        ownershipType = 'Sole Proprietor (individual owner)'
    else:
        ownershipType = 'Limited liability company (LLC)'
    for elem in WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#BusinessType-list > div.k-list-scroller'))).find_elements_by_tag_name('li'):
        if elem.text == ownershipType:
            elem.click()
            break
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.XPATH, '//span[@title="Identifier Type"]'))).send_keys('SSN')
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#Ssn'))).send_keys('1', Keys.BACKSPACE, business['officer']['SSN'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#ContactName_FirstName'))).send_keys(business['officer']['first name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#ContactName_LastName'))).send_keys(business['officer']['last name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#EmailAddress'))).send_keys(business['officer']['email'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#PhoneNumber_Number'))).send_keys('1', Keys.BACKSPACE, business['officer']['phone'])
    WDW(browser, 10).until(pres((By.XPATH, '//span[@title="A list of your recent previously used addresses."]'))).send_keys(business['address']['street1'][:3])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnAdd'))).click()
    time.sleep(1)
    browser.find_elements_by_tag_name('button')[-1].click()
    time.sleep(0.5)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#KnownByDifferentName_False'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#WasBusinessIssuedCertOrAccountNumber_False'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#SellProductsRetail'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#None'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()


    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#SellProductsAtRetail'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#None'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#None'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#None'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#None'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#None'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#None'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#None'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#IsEligible_False'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#SellTires_False'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#SellBatteries_False'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#SellCarSharingMemberships_False'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#OwnOrOperateDryCleaning_False'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#HasEmployeesInFlorida_False'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#HasEmployeesInFlorida_False'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#UsesContractors_False'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#IsEligible_False'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#ApplyingForDirectPayPermit_False'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#DoesEnterIntoWrittenObligations_False'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#OwnOrOperateGasDistributionFacility_False'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#ImportGasForOwnUse_False'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#IsEligible_False'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#WillFileAndPayElectronically_True'))).click()
    WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#EnrollmentType_3'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#AuthDorToSendEmail'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#ContactInformation_ContactName_FirstName'))).send_keys(business['officer']['first name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#ContactInformation_ContactName_LastName'))).send_keys(business['officer']['last name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#ContactInformation_EmailAddress'))).send_keys(business['officer']['email'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#ContactInformation_PhoneNumber_Number'))).send_keys('1', Keys.BACKSPACE, business['officer']['phone'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.XPATH, '//span[@aria-owns="ddlAvailableAuthorities_listbox"]'))).send_keys(business['officer']['last name'][:1])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#AuthorityConfirmation'))).click()
    WDW(browser, 10).until(pres((By.XPATH, '//span[@aria-owns="ddlAvailableSignatories_listbox"]'))).send_keys(business['officer']['last name'][:1])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()
    time.sleep(2)
    browser.find_elements_by_xpath('//button[@type="button" and @class="k-button k-primary"]')[-1].click()

    confirmationCode = WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#divDisplay_ConfirmationNumberFormatted'))).text
    record_the_output('Florida confirmation code: ' + confirmationCode)
    record_the_output('Florida email used for account registration: ' + addressForConfirmationEmails)


def connecticut():
    browser.get('https://drsbustax.ct.gov/AUT/welcomebusiness.aspx')
    WDW(browser, 10).until(pres((By.LINK_TEXT, 'Register New Business'))).click()
    time.sleep(0.5)
    browser.switch_to.window(browser.window_handles[1])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#radioBtn1'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    if business['type'] == 'Sole Proprietorship':
        Select(WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#ddlTypeOfOrg')))).select_by_visible_text('Single Member LLC (SMLLC)')
    else:
        Select(WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#ddlTypeOfOrg')))).select_by_visible_text('Limited Liability Company (LLC)')
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#chkBusDesc1'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#chkBusDesc2'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#txtMajorBusActivities'))).send_keys(business['nature of business'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#txtNAICSCode'))).send_keys(business['NAICS'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#txtOrgName'))).send_keys(business['name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#txtFEIN'))).send_keys(business['FEIN'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#txtBusTradeName'))).send_keys(business['name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#BusinessAddress_txtAddress1'))).send_keys(business['address']['street1'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#BusinessAddress_txtAddress2'))).send_keys(business['address']['street2'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#BusinessAddress_txtCity'))).send_keys(business['address']['city'])
    Select(WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#BusinessAddress_txtState')))).select_by_value(business['address']['state'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#BusinessAddress_txtZip'))).send_keys(business['address']['zip'][:5])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#chkBusLocationSame'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#txtBusinessPhone'))).send_keys(business['officer']['phone'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#rdoOwnerTypeIND'))).click()
    time.sleep(1)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#txtFirstName'))).send_keys(business['officer']['first name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#txtLastName'))).send_keys(business['officer']['last name'])
    Select(WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#ddlTitle1')))).select_by_value('OTH')
    WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#txtSSN'))).send_keys(business['officer']['SSN'].replace('-', ''))
    WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#txtDOB'))).send_keys(business['officer']['birth date'].strftime('%m/%d/%Y'))
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#HomeAddress1_txtAddress2'))).send_keys(business['officer']['address']['street2'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#HomeAddress1_txtAddress1'))).send_keys(business['officer']['address']['street1'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#HomeAddress1_txtAddress2'))).send_keys(business['officer']['address']['street2'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#HomeAddress1_txtCity'))).send_keys(business['officer']['address']['city'])
    Select(WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#HomeAddress1_txtState')))).select_by_value(business['officer']['address']['state'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#HomeAddress1_txtZip'))).send_keys(business['officer']['address']['zip'][:5])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#txtTelephone'))).send_keys(business['officer']['phone'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#txtBankName'))).send_keys(business['account']['bank name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#withholdingCmd_btnRegister'))).click()
    # answer "no" to all of them
    time.sleep(1)
    for radio in browser.find_elements_by_xpath('//input[starts-with(@id, "withholdingCmd__ctl0_tT") and contains(@value, "no")]'):
        if radio.is_displayed():
            radio.click()
    WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#withholdingCmd__ctl0_btnDone'))).click()

    # answer "no" to all of them and then answer "yes" to the first one
    time.sleep(1)
    for radio in browser.find_elements_by_xpath('//input[starts-with(@id, "salesCmd__ctl0_tT") and contains(@value, "no")]'):
        if radio.is_displayed():
            radio.click()
    WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#salesCmd__ctl0_tT3Q1yes'))).click()
    WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#salesCmd__ctl0_txtStart'))).send_keys(business['business commenced'].strftime('%m/%d/%Y'))
    WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#salesCmd__ctl0_btnDone'))).click()

    WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#PWFCmd__ctl0_tT13Q1no'))).click()
    WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#PWFCmd__ctl0_btnDone'))).click()

    WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#rocCmd__ctl0_tT7Q1no'))).click()
    WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#rocCmd__ctl0_btnDone'))).click()

    time.sleep(1)
    for radio in browser.find_elements_by_xpath('//input[starts-with(@id, "admitCmd__ctl0_tT") and contains(@value, "no")]'):
        if radio.is_displayed():
            radio.click()
    WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#admitCmd__ctl0_btnDone'))).click()

    WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#dryCleaingCmd__ctl0_tT6Q1no'))).click()
    WDW(browser, 10).until(pres((By.TAG_NAME, 'body'))).send_keys(Keys.ARROW_DOWN)
    time.sleep(0.6)
    WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#dryCleaingCmd__ctl0_btnDone'))).click()

    WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#tourismCmd__ctl0_tT8Q1no'))).click()
    WDW(browser, 10).until(pres((By.TAG_NAME, 'body'))).send_keys(Keys.ARROW_DOWN)
    time.sleep(0.6)
    WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#tourismCmd__ctl0_btnDone'))).click()

    WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#rentalCmd__ctl0_tT9Q1no'))).click()
    WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#rentalCmd__ctl0_btnDone'))).click()
    WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#cigaretteCmd__ctl0_tT13Q1no'))).click()
    WDW(browser, 10).until(pres((By.TAG_NAME, 'body'))).send_keys(Keys.ARROW_DOWN)
    time.sleep(0.6)
    WDW(browser, 10).until(clickable((By.CSS_SELECTOR, '#cigaretteCmd__ctl0_btnDone'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#rdoChecking'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#txtRoutingNumber'))).send_keys(business['account']['routing number'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#txtAccountNumber'))).send_keys(business['account']['account number'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#txtConfirmAccountNumber'))).send_keys(business['account']['account number'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#txtBankName'))).send_keys(business['account']['bank name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#rdoIATNo'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnNext'))).click()

    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#rdoYes'))).click()
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#txtFEINSSN'))).send_keys(business['FEIN'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#txtName'))).send_keys(business['officer']['first name'] + ' ' + business['officer']['last name'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#txtEmail'))).send_keys(business['officer']['email'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#txtDayPhone'))).send_keys(business['officer']['phone'])
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btn_Submit'))).click()

    confirmationCode = WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#divConf > strong'))).text.strip()
    record_the_output('Connecticut confirmation code: ' + confirmationCode)
    WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#btnExit'))).click()
    browser.close()
    browser.switch_to.window(browser.window_handles[0])


def california():
    browser.get('https://onlineservices.cdtfa.ca.gov/_/')
    WDW(browser, 10).until(pres((By.LINK_TEXT, 'Register a New Business Activity'))).click()

    california_field_fill([['checkbox', 'Selling items or goods in California', True]], False)
    button_click('Next')

    california_field_fill([
        ['radio', 'Alcoholic beverages', False],
        ['radio', 'Selling:\ncigarettes and/or tobacco products\nnicotine products', False],
        ['radio', 'Selling new tires', False],
        ['radio', 'Selling Covered Electronic Devices', False]
    ], False)
    button_click('Next')

    california_field_fill([
        ['radio', 'Fuel Products', False],
        ['radio', 'Selling lumber products', False],
        ['radio', 'Retail sales of prepaid wireless services', False],
        ['radio', 'Selling and/or manufacturing lead-acid batteries', False]
    ], False)
    button_click('Next')

    if business['type'] == 'Sole Proprietorship':
        ownershipType = 'Individual/Sole Proprietor'
    else:
        ownershipType = 'Limited Liability Company (LLC)'
    california_field_fill([['select', 'What Business type are you registering this activity for', ownershipType]], False)
    button_click('Next')

    california_field_fill([
        ['select', 'Primary Identification Type', 'SSN'],
        ['text', 'SSN', business['officer']['SSN']],
        ['selectValue', 'State', business['officer']['drivers license state']],
        ['text', 'Driver\'s License Number', business['officer']['drivers license']],
        ['radio', 'Are you changing from one type of business entity to another', False]
    ], False)
    button_click('Next')

    california_field_fill([['radio', 'Do you have a current account with CDTFA', False]], False)
    button_click('Next')

    time.sleep(1)
    button_click('Next')

    california_field_fill([['radio', 'Are you applying for Temporary', False]], False)
    button_click('Next')

    california_field_fill([
        ['text', 'Street', business['address']['street1']],
        ['text', 'City', business['address']['city']],
        ['selectValue', 'State', business['address']['state']],
        ['text', 'Zip', business['address']['zip']]
    ], False)
    button_click('Click Here to Verify Address')
    time.sleep(1)
    if 'Verified' in browser.find_element_by_tag_name('html').text:
        browser.find_elements_by_xpath('//tr[@class="DataRow TDRE"]')[0].click()
        time.sleep(1)
    button_click('Next')

    california_field_fill([
        ['text', 'First Name', business['officer']['first name']],
        ['text', 'Last Name', business['officer']['last name']],
        ['text', 'Date of Birth', business['officer']['birth date'].strftime('%m/%d/%Y')],
        ['text', 'Phone Number', business['officer']['phone']],
        ['textLatest', 'Email Address', business['officer']['email']],
        ['text', 'Confirm Email Address', business['officer']['email']]
    ], False)
    button_click('Next')

    WDW(browser, 10).until(pres((By.LINK_TEXT, 'Add'))).click()
    Select(WDW(browser, 10).until(pres((By.XPATH, '//select[@class="AttachmentInput FieldRequired"]')))).select_by_value('SUPPL')
    WDW(browser, 10).until(pres((By.XPATH, '//input[@class="AttachmentInput FieldRequired"]'))).send_keys('ID')
    attachmentPath = ''
    for fileName in os.listdir(os.path.join(user_path, 'California - applicants ID')):
        if fileName.lower().endswith('.jpg') or fileName.lower().endswith('.png') or fileName.lower().endswith('.jpeg'):
            attachmentPath = os.path.join(user_path, 'California - applicants ID', fileName)
    WDW(browser, 10).until(pres((By.XPATH, '//input[@id="AttachmentFile"]'))).send_keys(attachmentPath)
    button_click('Save')
    i = 0
    while i < 15:
        i += 1
        time.sleep(2)
        if len(browser.find_elements_by_link_text('Remove')) > 1:
            break
    button_click('Next')

    california_field_fill([
        ['radio', 'Books and records maintained by owner?', True],
        ['radio', 'Is the owner the contact for business activities?', True]
    ], False)
    button_click('Next')

    california_field_fill([
        ['radio', 'Will the business be accepting credit card payments?', False],
        ['radio', 'Are you making internet sales?', True]
    ], False)
    california_field_fill([['radio', 'Are you making internet sales through a third party?', False]], False)
    for table in browser.find_elements_by_xpath('//table[@role="grid"]'):
        if 'Please provide your business website' in table.text:
            table.find_element_by_xpath('tbody/tr/td[2]/div').click()
            break
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and starts-with(@class, "TDC")]'))).send_keys(business['supplier']['website'])
    button_click('Next')

    WDW(browser, 10).until(pres((By.LINK_TEXT, 'Add NAICS Code'))).click()
    WDW(browser, 10).until(pres((By.XPATH, '//input[starts-with(@class, "FieldEnabled FieldRequired DocControlText")]'))).send_keys(business['NAICS'])
    button_click('Search')
    while True:
        time.sleep(1)
        elems = browser.find_elements_by_link_text(business['NAICS'])
        if not elems:
            WDW(browser, 10).until(pres((By.LINK_TEXT, 'Next Page'))).click()
            time.sleep(1)
            continue
        elems[0].click()
        break
    button_click('OK')
    button_click('Next')

    for elem in browser.find_elements_by_xpath('//fieldset[starts-with(@class, "FastComboButtonSet")]'):
        if elem.is_displayed():
            elem.find_elements_by_tag_name('label')[1].click()
    button_click('Next')

    california_field_fill([
        ['radio', 'Do you have a retail location, stock of goods, or warehouse in California', False],
        ['radio', 'Are you registering since your business has economic nexus in California', True]
    ], True)
    button_click('Next')

    california_field_fill([['radio', 'Are you installing or leasing equipment in California', False]], False)
    button_click('Next')

    california_field_fill([
        ['text', 'Start Date', business['business commenced'].strftime('%m/%d/%Y')],
        ['text', 'Projected Monthly Sales', business['projected monthly sales']],
        ['text', 'Projected Monthly Taxable Sales', business['projected monthly sales']],
        ['textarea', 'Products that will be sold during the course of business', business['nature of business']],
        ['radio', 'Do you have independent sales representative(s) in California?', False]
    ], False)
    button_click('Next')

    california_field_fill([
        ['checkbox', 'Select a Books and Records Address for the Sales and Use Tax Account', True],
        ['checkbox', 'Select a Mailing Address for the Sales and Use Tax Account', True]
    ], False)
    button_click('Next')

    WDW(browser, 10).until(pres((By.LINK_TEXT, 'Add a Record'))).click()
    time.sleep(2)
    california_field_fill([
        ['text', 'Name', business['supplier']['name']],
        ['text', 'Phone Number', business['supplier']['phone']],
        ['textarea', 'Products Purchased', business['supplier']['products purchased']],
        ['text', 'Street', business['supplier']['address']['street1']],
        ['text', 'Street 2', business['supplier']['address']['street2']],
        ['text', 'City', business['supplier']['address']['city']],
        ['selectValue', 'State', business['supplier']['address']['state']],
        ['text', 'Zip', business['supplier']['address']['zip']],
    ], False)
    button_click('Click Here to Verify Address')
    time.sleep(2)
    WDW(browser, 10).until(pres((By.LINK_TEXT, 'Click here to verify address'))).click()
    time.sleep(1)
    button_click('Save')
    button_click('Add')
    button_click('Next')

    california_field_fill([['radio', 'I acknowledge that I have read', True]], False)
    button_click('Next')

    california_field_fill([
        ['text', 'Name', business['officer']['first name'] + ' ' + business['officer']['last name']],
        ['selectValue', 'What is your role in this application?', 'Other'],
        ['text', 'Email Address', business['officer']['email']],
        ['text', 'Confirm Email', business['officer']['email']],
        ['textLatest', 'Phone', business['officer']['phone']]
    ], False)
    button_click('Next')

    california_field_fill([['checkbox', 'By checking this, I am declaring my', True]], False)
    button_click('Next')

    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="radio"]')))
    browser.find_elements_by_xpath('//input[@type="radio"]')[2].click()
    button_click('Next')

    button_click('Submit')
    button_click('OK')

    i = 0
    while i < 15:
        i += 1
        if 'This request has been submitted and is being processed.' in browser.page_source:
            text = browser.find_element_by_tag_name('html').text
            confirmationCode = text.split('confirmation number:')[1].split('.')[0].strip()
            record_the_output('California confirmation code: ' + confirmationCode)


def massachusetts():
    browser.get('https://mtc.dor.state.ma.us/mtc/_/')
    WDW(browser, 10).until(pres((By.LINK_TEXT, 'Register a New Taxpayer'))).click()
    WDW(browser, 10).until(pres((By.LINK_TEXT, 'Register a Business'))).click()
    massachusetts_button_click('#action_6')

    massachusetts_field_fill([
        ['select', 'Select Reason', 'BusOrgOth']
    ], False)
    massachusetts_button_click('#action_6')

    if business['type'] == 'Sole Proprietorship':
        ownershipType = 'SolePr'
    else:
        ownershipType = 'LLC'
    Select(WDW(browser, 10).until(pres((By.TAG_NAME, 'select')))).select_by_value(ownershipType)

    massachusetts_field_fill([
        ['radio', 'Are you a nonprofit business/organization?', True]
    ], False)
    massachusetts_button_click('#action_6')

    massachusetts_field_fill([
        ['text', 'Business Start Date', business['business commenced'].strftime('%d-%b-%Y')],
        ['select', 'ID Type', 'SSN'],
        ['text', 'ID', business['officer']['SSN']],
        ['text', 'First Name', business['officer']['first name']],
        ['text', 'Last Name', business['officer']['last name']]
    ], False)
    massachusetts_button_click('#action_6')

    massachusetts_field_fill([
        ['text', 'Street', business['supplier']['address']['street1']],
        ['text', 'City', business['supplier']['address']['city']],
        ['select', 'State', business['supplier']['address']['state']],
        ['text', 'Zip Code', business['supplier']['address']['zip']],
        ['radio', 'Is your legal address also your mailing address?', False]
    ], False)
    button_click('Verify Address')
    if 'No valid address was found' in browser.find_element_by_tag_name('html').text:
            raise Exception('Address not found for ' + str(business['address']))
    elif 'Select this address' in browser.find_element_by_tag_name('html').text:
        click_and_compare('partial text', 'As Entered')
        # confirm selecting unverified address:
        button_click('Yes')

    time.sleep(1)
    massachusetts_button_click('#action_6')

    massachusetts_button_click('#action_6')

    massachusetts_field_fill([
        ['checkbox', 'Sales Tax', True],
        ['checkbox', 'Use Tax', True],
    ], False)
    massachusetts_button_click('#action_6')

    massachusetts_field_fill([['text', 'Keyword', business['NAICS'][:5]]], False)
    button_click('Search')
    i = 0
    while i < 3:
        i += 1
        time.sleep(2)
        elems = browser.find_elements_by_link_text(business['NAICS'][:5])
        nextButtons = browser.find_elements_by_xpath('//a[@title="Go to the next page"]')
        if elems or nextButtons:
            break

    while True:
        if not elems:
            WDW(browser, 10).until(pres((By.XPATH, '//a[@title="Go to the next page"]'))).click()
            time.sleep(2)
            elems = browser.find_elements_by_link_text(business['NAICS'][:5])
            continue
        elems[0].click()
        break
    massachusetts_button_click('#action_6')

    massachusetts_field_fill([
        ['text', 'Date you are first required', business['business commenced'].strftime('%d-%b-%Y')],
        ['text', 'Street', business['supplier']['address']['street1']],
        ['text', 'City', business['supplier']['address']['city']],
        ['select', 'State', business['supplier']['address']['state']],
        ['text', 'Zip Code', business['supplier']['address']['zip']],
    ], False)
    button_click('Verify Address')
    if 'No valid address was found' in browser.find_element_by_tag_name('html').text:
            raise Exception('Address not found for ' + str(business['address']))
    elif 'Select this address' in browser.find_element_by_tag_name('html').text:
        click_and_compare('partial text', 'As Entered')
        # confirm selecting unverified address:
        button_click('Yes')
    massachusetts_button_click('#action_6')

    massachusetts_field_fill([
        ['text', 'Date that first purchase was made', business['business commenced'].strftime('%d-%b-%Y')]
    ], False)
    massachusetts_button_click('#action_6')

    massachusetts_field_fill([
        ['text', 'Date you are first required to collect Massachusetts taxes', business['business commenced'].strftime('%d-%b-%Y')]
    ], False)
    for elem in browser.find_elements_by_xpath('//div[@class="FGFC FGCPLeft CTEC FGControlRadioButton FieldEnabled FieldError"]'):
        if elem.text == 'No':
            while True:
                try:
                    elem.find_element_by_tag_name('input').click()
                    time.sleep(0.5)
                    break
                except:
                    browser.find_element_by_tag_name('html').send_keys(Keys.PAGE_DOWN)
                    time.sleep(1)
    for elem in browser.find_elements_by_xpath('//div[@class="FGFC FGCPLeft CTEC FGControlRadioButton FieldEnabled FieldError"]'):
        if elem.text == 'No':
            i = 0
            while i < 5:
                i += 1
                try:
                    elem.find_element_by_tag_name('input').click()
                    time.sleep(0.5)
                    break
                except ElementClickInterceptedException:
                    browser.find_element_by_tag_name('html').send_keys(Keys.PAGE_DOWN)
                    time.sleep(1)
    time.sleep(3)
    for elem in browser.find_elements_by_xpath('//div[@class="FGFC FGCPLeft CTEC FGControlRadioButton FieldEnabled FieldError"]'):
        if elem.text == '$1,201+':
            i = 0
            while i < 5:
                i += 1
                try:
                    elem.find_element_by_tag_name('input').click()
                    time.sleep(0.5)
                    break
                except ElementClickInterceptedException:
                    browser.find_element_by_tag_name('html').send_keys(Keys.PAGE_DOWN)
                    time.sleep(1)
    massachusetts_button_click('#action_6')
    pin = ''.join(random.choice('1234567890') for x in range(4))
    record_the_output('Massachucetts PIN: ' + pin)

    massachusetts_field_fill([
        ['text', 'Full Name', business['officer']['first name'] + ' ' + business['officer']['last name']],
        ['text', 'Create a 4-digit PIN', pin],
        ['text', 'E-mail Address', business['officer']['email']],
        ['text', 'Confirm E-mail', business['officer']['email']],
        ['text', 'Phone Number', business['officer']['phone']],
    ], False)
    massachusetts_button_click('#action_6')

    massachusetts_field_fill([
        ['text', 'Username', username],
        ['text', 'Password', password],
        ['text', 'Confirm Password', password],
    ], False)
    Select(browser.find_element_by_tag_name('select')).select_by_value('SQ6')
    browser.find_elements_by_xpath('//input[@type="password"]')[-1].send_keys(hintAnswer)
    massachusetts_button_click('#action_6')

    massachusetts_button_click('#action_6')


    browser.find_element_by_tag_name('html').send_keys(Keys.END)
    time.sleep(1)
    elem = WDW(browser, 10).until(pres((By.XPATH, '//input[@type="checkbox"]')))
    elem.send_keys(Keys.ENTER)
    elem.send_keys(Keys.SPACE)
    massachusetts_button_click('#action_6')

    massachusetts_button_click('#action_8')
    text = WDW(browser, 10).until(pres((By.TAG_NAME, 'html'))).text
    confirmationCode = text.split('Confirmation Number:')[1].split('\n')[0].strip()
    record_the_output('Massachusetts confirmation code: ' + confirmationCode)


def maryland():
    browser.get('https://interactive.marylandtaxes.gov/webapps/comptrollercra/entrance.asp')
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="image" and @name="reg_button"]'))).click()
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="checkbox" and @value="Sales and Use Tax"]'))).click()
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="image"]'))).click()

    if business['type'] == 'Sole Proprietorship':
        WDW(browser, 10).until(pres((By.XPATH, '//input[@type="radio" and contains(@onclick, "Sole Proprietorship")]'))).click()
    else:
        WDW(browser, 10).until(pres((By.XPATH, '//input[@type="radio" and contains(@onclick, "Limited Liability Corporation")]'))).click()
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="radio" and @name="PayingWages" and @value="No"]'))).click()
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and @name="FedIdNum_Part1"]'))).send_keys(business['FEIN'][:2])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and @name="FedIdNum_Part2"]'))).send_keys(business['FEIN'][2:])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and @name="SSNTaxOfficer_Part1"]'))).send_keys(business['officer']['SSN'].replace('-', '')[:3])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and @name="SSNTaxOfficer_Part2"]'))).send_keys(business['officer']['SSN'].replace('-', '')[3:5])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and @name="SSNTaxOfficer_Part3"]'))).send_keys(business['officer']['SSN'].replace('-', '')[5:])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and @name="NameofTaxOfficer"]'))).send_keys(business['officer']['first name'] + ' ' + business['officer']['last name'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and @name="LegalName"]'))).send_keys(business['name'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and @name="LocationAddress1"]'))).send_keys(business['address']['street1'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and @name="LocationAddress2"]'))).send_keys(business['address']['street2'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and @name="LocationCity"]'))).send_keys(business['address']['city'])
    if business['address']['state'] == 'MD':
        Select(WDW(browser, 10).until(pres((By.XPATH, '//select[@name="LocationCounty"]')))).select_by_visible_text(business['address']['county'].upper() + ' COUNTY')
    elif business['address']['state'] == 'DC':
        Select(WDW(browser, 10).until(pres((By.XPATH, '//select[@name="LocationCounty"]')))).select_by_visible_text('DISTRICT OF COLUMBIA (DC)')
    else:
        Select(WDW(browser, 10).until(pres((By.XPATH, '//select[@name="LocationCounty"]')))).select_by_visible_text('OUT OF STATE')
    Select(WDW(browser, 10).until(pres((By.XPATH, '//select[@name="LocationState"]')))).select_by_value(business['address']['state'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and @name="LocationZipCode"]'))).send_keys(business['address']['zip'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and @name="PhoneNum_Part1"]'))).send_keys(business['officer']['phone'][:3])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and @name="PhoneNum_Part2"]'))).send_keys(business['officer']['phone'][3:6])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and @name="PhoneNum_Part3"]'))).send_keys(business['officer']['phone'][6:])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and @name="EmailAddress"]'))).send_keys(business['officer']['email'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="image"]'))).click()

    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="radio" and @name="BusOpGeneralCode" and @value="9"]'))).click()
    Select(WDW(browser, 10).until(pres((By.XPATH, '//select[@name="BusOpSpecificCode"]')))).select_by_visible_text('Miscellaneous Use Tax')
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="radio" and @name="OnlineSales" and @value="O"]'))).click()
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="image"]'))).click()

    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="radio" and starts-with(@name, "Employee") and @value="No"]'))).click()
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="image"]'))).click()

    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="checkbox" and @name="BusinessType" and @value="New Business"]'))).click()
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="image"]'))).click()

    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="radio" and @name="Acquisition" and @value="No"]'))).click()
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="image"]'))).click()

    WDW(browser, 10).until(pres((By.XPATH, '//textarea[@name="BusinessActivityDescription"]'))).send_keys(business['nature of business'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="radio" and @name="PrimarySupportService" and @value="No"]'))).click()
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="radio" and @name="MultipleMDLocations" and @value="No"]'))).click()
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="image"]'))).click()

    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and @name="PreparersName"]'))).send_keys(business['officer']['first name'] + ' ' + business['officer']['last name'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and @name="PreparersPhoneNum_Part1"]'))).send_keys(business['officer']['phone'][:3])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and @name="PreparersPhoneNum_Part2"]'))).send_keys(business['officer']['phone'][3:6])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and @name="PreparersPhoneNum_Part3"]'))).send_keys(business['officer']['phone'][6:])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="text" and @name="PreparersEmail"]'))).send_keys(business['officer']['email'])
    WDW(browser, 10).until(pres((By.XPATH, '//input[@type="image" and @name="Submit" and @value="Submit Application"]'))).click()

    text = browser.find_element_by_tag_name('html').text
    confirmationCode = text.split('confirmation number for this application is')[1].split('Please print or save')[0].strip()
    record_the_output('Maryland confirmation code: ' + confirmationCode)


if getattr(sys, 'frozen', False):
    application_path = os.path.abspath(os.path.dirname(sys.executable))
    user_path = os.path.join(os.path.split(application_path)[0])
else:
    application_path = os.path.abspath(os.path.dirname(__file__))
    user_path = application_path

appLaunchTimeSpamp = datetime.datetime.now().strftime('%b %d %Y %H-%M')

if 'logs' not in os.listdir(user_path):
    os.mkdir(os.path.join(user_path, 'logs'))
reportName = os.path.join(user_path, 'logs', 'log ' + appLaunchTimeSpamp + '.txt')
logging.basicConfig(filename=reportName, level=logging.INFO, format=' %(asctime)s -  %(levelname)s -  %(message)s')

credentialsFileName = 'gmail credentials.txt'
if credentialsFileName not in os.listdir(user_path):
    emailAccount = input('Please paste your gmail address and press Enter: ').strip()
    emailPassword = input('Please paste your gmail password and press Enter: ').strip()
    print(f'Thanks. They will be stored in plain text in the file "{credentialsFileName}"')
    lastEmailSuffix = '+1'
    json.dump([emailAccount, emailPassword, lastEmailSuffix], open(os.path.join(user_path, credentialsFileName), 'w'))
else:
    emailAccount, emailPassword, lastEmailSuffix = json.load(open(os.path.join(user_path, credentialsFileName)))
newEmailSuffix = '+' + str(int(lastEmailSuffix.strip('+ ')) + 1)
addressForConfirmationEmails = emailAccount.split('@')[0] + newEmailSuffix + '@' + emailAccount.split('@')[1]
json.dump([emailAccount, emailPassword, newEmailSuffix], open(os.path.join(user_path, credentialsFileName), 'w'))

stateCodes = {
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'DC': 'District of Columbia',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'IA': 'Iowa',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MS': 'Mississippi',
    'MO': 'Missouri',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming'
}

naicsCodes = json.load(open(os.path.join(application_path, 'NAICS codes')))

thatFileName = ''
for fileName in os.listdir(user_path):
    if fileName.lower().endswith('.csv'):
        thatFileName = fileName
data = list(csv.reader(open(os.path.join(user_path, thatFileName))))

try:
    business = {
        'type': data[1][1],  # can be 'Sole Proprietorship' or 'Limited Liability Company'
        'FEIN': data[22][1],
        'name': data[26][1],
        'address': {
            'street1': data[14][1],
            'street2': '',
            'city': data[15][1],
            'county': data[18][1],
            'state': data[16][1],
            'zip': data[17][1]
        },
        'business commenced': datetime.datetime.strptime(data[33][1], '%m/%d/%Y'),
        'NAICS': data[63][1],
        'nature of business': data[64][1],
        'projected monthly sales': data[65][1],
        'account': {
            'bank name': data[30][1],
            'routing number': data[31][1],
            'account number': data[32][1]
        },
        'officer': {
            'birth date': datetime.datetime.strptime(data[7][1], '%m/%d/%Y'),
            'commence': datetime.datetime.strptime(data[66][1], '%m/%d/%Y'),
            'cease': datetime.datetime.strptime(data[67][1], '%m/%d/%Y'),
            'SSN': data[23][1],
            'first name': data[2][1],
            'last name': data[4][1],
            'email': data[5][1],
            'phone': data[19][1],
            'drivers license state': data[25][1],
            'drivers license': data[24][1],
            'address': {
                'street1': data[14][1],
                'street2': '',
                'city': data[15][1],
                'county': data[18][1],
                'state': data[16][1],
                'zip': data[17][1]
            },
        },
        'supplier': {
            'name': 'WALMART',
            'website': 'WALMART.COM',
            'phone': '6023476030',
            'products purchased': 'Misc. durable goods',
            'address': {
                'street1': '702 SW 8TH ST',
                'street2': '',
                'city': 'BENTONVILLE',
                'state': 'AR',
                'zip': '72716-0001'
            },
        }
    }
except:
    logging.error(traceback.format_exc())
    print('\nSome data in the file is filled incorrectly. Press Enter to exit\n')
    print(traceback.format_exc().split('\n')[-2])
    input()
    quit()

# credentials for all websites
username = business['officer']['first name'][:10] + '0' + random_string_generator(4).lower()
password = random_string_generator(10) + '0!'

hintAnswer = random_string_generator(10)  # the answer to question like "What is the name of your first pet?"
numRetries = 3  # number of retries for each website before it returns an error

initialText = f'Data used on all websites: \n' \
              f'Username: {username}\n' \
              f'Password: {password}\n' \
              f'Hint answer (for questions like what is the name of your first pet): {hintAnswer}'
record_the_output(hintAnswer)

print(f'If you would like to register the business {business["name"]} in all states, press Enter')
print('If you would like to select certain states, type any letter and press Enter')
userInput = input()
stateOptions = [
    ['1', 'District of Columbia'],
    ['2', 'Mississippi'],
    ['3', 'Tennessee'],
    ['4', 'Florida'],
    ['5', 'Connecticut'],
    ['6', 'California'],
    ['7', 'Massachusetts'],
    ['8', 'Maryland'],
    ['9', 'Missouri'],
    ['10', 'Kansas']
]
selectedStates = {}
if userInput:
    print('Type numbers of all states you would like to apply in and press Enter. No spaces, separated with comma: 1,3,4,10')
    for option in stateOptions:
        print(option[0] + '. ' + option[1])
    userInput = input()
    for option in stateOptions:
        if option[0] in userInput.strip().split(','):
            selectedStates[option[1]] = True
        else:
            selectedStates[option[1]] = False
else:
    for option in stateOptions:
        selectedStates[option[1]] = True


options = Options()
driver_path = os.path.join('C:\\Users\\baban\\PycharmProjects', 'chromedriver.exe')
# options.binary_location = 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'
options.add_argument("--start-maximized")
options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
options.add_argument('--disable-blink-features=AutomationControlled')
browser = webdriver.Chrome(options=options, executable_path=driver_path)

# get the county for the given address
for address in [business['address']]:
    if not address.get('county', ''):
        browser.get('https://www.unitedstateszipcodes.org/')
        WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#q'))).send_keys(address['street1'] + ' ' + address['city'] + ' ' + address['state'])
        WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#search-forms > div.col-xs-12.col-lg-7 > div > span.input-group-btn > button'))).click()
        for elem in WDW(browser, 10).until(pres((By.CSS_SELECTOR, '#map-info > table'))).find_elements_by_tag_name('tr'):
            if 'County:' in elem.text:
                county = elem.text.split('County:')[1].strip()
                break
        address['county'] = county

# if selectedStates['Missouri']:
#     i = 0
#     print('Filling the form on Missouri website')
#     while i < numRetries:
#         i += 1
#         try:
#             missouri()
#             break
#         except:
#             print('Something went wrong, retrying...')
#             logging.error(traceback.format_exc())
#             if i == numRetries - 1:
#                 print('Could not fill the form. Please send the latest log (in the "logs" folder) to the developer')
#                 logging.error('Could not fill the form after all retries')
#             browser.quit()
#             browser = webdriver.Chrome(options=options, executable_path=driver_path)
#
# if selectedStates['Kansas']:
#     i = 0
#     print('Filling the form on Kansas website')
#     while i < numRetries:
#         i += 1
#         try:
#             kansas()
#             break
#         except:
#             print('Something went wrong, retrying...')
#             logging.error(traceback.format_exc())
#             if i == numRetries - 1:
#                 print('Could not fill the form. Please send the latest log (in the "logs" folder) to the developer')
#                 logging.error('Could not fill the form after all retries')
#             browser.quit()
#             browser = webdriver.Chrome(options=options, executable_path=driver_path)

if selectedStates['District of Columbia']:
    i = 0
    print('Filling the form on District of Columbia website')
    while i < numRetries:
        i += 1
        try:
            district_of_columbia()
            break
        except:
            print('Something went wrong, retrying...')
            logging.error(traceback.format_exc())
            if i == numRetries - 1:
                print('Could not fill the form. Please send the latest log (in the "logs" folder) to the developer')
                logging.error('Could not fill the form after all retries')
            browser.quit()
            browser = webdriver.Chrome(options=options, executable_path=driver_path)

if selectedStates['Mississippi']:
    i = 0
    print('Filling the form on Mississippi website')
    while i < numRetries:
        i += 1
        try:
            mississippi()
            break
        except:
            print('Something went wrong, retrying...')
            logging.error(traceback.format_exc())
            if i == numRetries - 1:
                print('Could not fill the form. Please send the latest log (in the "logs" folder) to the developer')
                logging.error('Could not fill the form after all retries')
            browser.quit()
            browser = webdriver.Chrome(options=options, executable_path=driver_path)
            if 'This FEIN already registered in Mississippi' in traceback.format_exc():
                record_the_output('Mississippi website was skipped because it says this FEIN is already registered there')
                break

if selectedStates['Tennessee']:
    i = 0
    print('Filling the form on Tennessee website')
    while i < numRetries:
        i += 1
        try:
            tennessee()
            break
        except:
            print('Something went wrong, retrying...')
            logging.error(traceback.format_exc())
            if i == numRetries - 1:
                print('Could not fill the form. Please send the latest log (in the "logs" folder) to the developer')
                logging.error('Could not fill the form after all retries')
            browser.quit()
            browser = webdriver.Chrome(options=options, executable_path=driver_path)

if selectedStates['Florida']:
    i = 0
    print('Filling the form on Florida website')
    while i < numRetries:
        i += 1
        try:
            florida()
            break
        except:
            print('Something went wrong, retrying...')
            logging.error(traceback.format_exc())
            if i == numRetries - 1:
                print('Could not fill the form. Please send the latest log (in the "logs" folder) to the developer')
                logging.error('Could not fill the form after all retries')
            browser.quit()
            browser = webdriver.Chrome(options=options, executable_path=driver_path)

if selectedStates['Connecticut']:
    i = 0
    print('Filling the form on Connecticut website')
    while i < numRetries:
        i += 1
        try:
            connecticut()
            break
        except:
            print('Something went wrong, retrying...')
            logging.error(traceback.format_exc())
            if i == numRetries - 1:
                print('Could not fill the form. Please send the latest log (in the "logs" folder) to the developer')
                logging.error('Could not fill the form after all retries')
            browser.quit()
            browser = webdriver.Chrome(options=options, executable_path=driver_path)

if selectedStates['California']:
    i = 0
    print('Filling the form on California website')
    while i < numRetries:
        i += 1
        try:
            california()
            break
        except:
            print('Something went wrong, retrying...')
            logging.error(traceback.format_exc())
            if i == numRetries - 1:
                print('Could not fill the form. Please send the latest log (in the "logs" folder) to the developer')
                logging.error('Could not fill the form after all retries')
            browser.quit()
            browser = webdriver.Chrome(options=options, executable_path=driver_path)

if selectedStates['Massachusetts']:
    i = 0
    print('Filling the form on Massachusetts website')
    while i < numRetries:
        i += 1
        try:
            massachusetts()
            break
        except:
            print('Something went wrong, retrying...')
            logging.error(traceback.format_exc())
            if i == numRetries - 1:
                print('Could not fill the form. Please send the latest log (in the "logs" folder) to the developer')
                logging.error('Could not fill the form after all retries')
            browser.quit()
            browser = webdriver.Chrome(options=options, executable_path=driver_path)

if selectedStates['Maryland']:
    i = 0
    print('Filling the form on Maryland website')
    while i < numRetries:
        i += 1
        try:
            maryland()
            break
        except:
            print('Something went wrong, retrying...')
            logging.error(traceback.format_exc())
            if i == numRetries - 1:
                print('Could not fill the form. Please send the latest log (in the "logs" folder) to the developer')
                logging.error('Could not fill the form after all retries')
            browser.quit()
            browser = webdriver.Chrome(options=options, executable_path=driver_path)
