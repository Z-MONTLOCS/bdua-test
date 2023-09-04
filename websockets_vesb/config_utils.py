from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import time
import asyncio


#***************************************************
#***************************************************
#***************************************************

async def initialize_driver():

    prefs = {

    "profile.default_content_setting_values": {
        "images": 2,  
        "javascript": 2, 
        "css": 2, 
        "plugins": 2, 
    }

    }    

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_experimental_option("prefs", prefs)
    #chrome_options.add_argument("--start-minimize") 
    chrome_options.add_argument("--disable-popup-blocking")  


    path = 'C:/Users/chromedriver-win64/chromedriver.exe'
    service = Service(path)

    try:
        loop = asyncio.get_event_loop()
        driver = await loop.run_in_executor(None, lambda: webdriver.Chrome(options=chrome_options, service=service))
        
        website = 'https://aplicaciones.adres.gov.co/bdua_internet/Pages/ConsultarAfiliadoWeb.aspx'
        await loop.run_in_executor(None, lambda: driver.get(website))
        
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, 'btnConsultar'))
            )
            #print("Página cargada correctamente.")

            
            return driver
        except Exception as e:
            # print("Error al cargar la página:")
            error_page="Error al cargar la página:"
            driver.quit()
         
            return error_page 

    except Exception as e:
        # print("Error al inicializar el controlador  confi:", e)
        error_driver ="Error al inicializar el controlador:"
       

        return error_driver

#***************************************************
#***************************************************
#***************************************************

async def set_data_query(driver, datos):

    document_type = datos.get('documentType')
    identification_number = datos.get('identificationNumber')

    print("============Datos recibidos Cliente=================")
    print(" ")
    print("Tipo de documento:", document_type)
    print("Número de identificación:", identification_number)
    print("=================================================")
    print(" ")

    elemento_select = driver.find_element(By.ID, "tipoDoc")
    select = Select(elemento_select)
    select.select_by_value(document_type)

    elemento_input = driver.find_element(By.ID, "txtNumDoc")
    elemento_input.send_keys(identification_number)

    await focus_input_code(driver)

    erro_input_number = await get_forms_error(driver)

    if erro_input_number == "Número de Identificación No Válida.":

        # print("Número de identificación:", identification_number)

        return erro_input_number
    
    else:

        #  print("Número de identificación:", identification_number)

         return None

#***************************************************
#***************************************************
#***************************************************

async def get_url_captcha_image(driver):
    try:
        elemento_img = driver.find_element(By.ID, 'Capcha_CaptchaImageUP') 

        # print("Elemento de imagen :", elemento_img.get_attribute('src'))
        return elemento_img.get_attribute('src')
     

    except NoSuchElementException as e:
        # print("Elemento de imagen no encontrado:", e)
        #driver.quit()
        raise

    except TimeoutException as e:
        # print(" ")  
        # print(" ******* erorr ********* ")  
        # print("Tiempo de espera agotado:", e)
        # print(" ******* erorr ********* ")  
        # print(" ")  
        #driver.quit()
        raise   

#***************************************************
#***************************************************
#***************************************************

async def validate_code(driver):

    time.sleep(2)

    elemento_span = driver.find_element(By.XPATH, ' /html/body/div/form/div[4]/div/div/span')

    #elemento_span = driver.find_element(By.ID, 'Capcha_ctl00')
    texto_span = elemento_span.text

    return texto_span

#***************************************************
#***************************************************
#***************************************************

async def focus_input_code(driver):
     elemento_input = driver.find_element(By.ID, 'Capcha_CaptchaTextBox')
     time.sleep(2)
     elemento_input.click()

#***************************************************
#***************************************************
#***************************************************

async def set_code(driver, datos):
    code = datos.get('code')

    #socket_id = datos.get('socket_id')
    
    # print("============Datos recibidos Cliente=================")
    # print(" ")
    # print("socket_id:", socket_id)
    # print("code:", code)
  
    # print("=================================================")
    # print(" ")
    elemento_input = driver.find_element(By.ID, 'Capcha_CaptchaTextBox')

    elemento_input.send_keys(code)
    elemento_input = driver.find_element(By.ID, 'btnConsultar')
    time.sleep(2)
    elemento_input.click()
    time.sleep(2)




    erro_input_code = await validate_code(driver)

    if erro_input_code == "El codigo ingresado no es valido":

        # print("El codigo ingresado no es valido:", erro_input_code)

        return erro_input_code
    
    else:

        #  print("codigo correcto:", erro_input_code)

         return None

#***************************************************
#***************************************************
#***************************************************

async def get_forms_error(driver):
    time.sleep(2)

    elemento_span = driver.find_element(By.XPATH, '/html/body/div/form/div[4]/span[3]')

    # print("Texto del elemento:", elemento_span.text)

    # elemento_span = driver.find_element(By.ID, 'RegularExpressionValidator1')
    error = elemento_span.text
    return error      

#***************************************************
#***************************************************
#***************************************************

async def get_new_tab(driver):
    driver.switch_to.window(driver.window_handles[-1])

#***************************************************
#***************************************************
#***************************************************

async def get_personal_data(driver):
    try:
        data_table = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, 'GridViewBasica'))
        )

        data_info = {}

        container_element = driver.find_element(By.CLASS_NAME, 'center')
        rows = container_element.find_elements(By.TAG_NAME, 'tr')

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) == 2:
                key = cells[0].text
                value = cells[1].text
                data_info[key] = value

        return data_info

    except NoSuchElementException:
      
        elemento_span = driver.find_element(By.XPATH, '  /html/body/form/div[3]/div[3]/span')

        #elemento_span = driver.find_element(By.ID, 'lblError')
        elemento_span_text = elemento_span.text

        #print(f"Usuario no existe: {elemento_span_text}")

       


    except TimeoutException:
        #print("La tabla no está presente en la página.")
        return None

#***************************************************
#***************************************************
#***************************************************

async def get_affiliation_data(driver):
    try:
        affiliation_table = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, 'GridViewAfiliacion'))
        )
        
        affiliation_info = {}
        affiliation_rows = affiliation_table.find_elements(By.TAG_NAME, 'tr')

        for affiliation_row in affiliation_rows:
            affiliation_cells = affiliation_row.find_elements(By.TAG_NAME, 'td')
    
            if len(affiliation_cells) == 6:
                keys = ['Status', 'EPS', 'Regime', 'Effective Date', 'End Date', 'Affiliate Type']
        
                for i, key in enumerate(keys):
                    affiliation_info[key] = affiliation_cells[i].text

        return affiliation_info

    except NoSuchElementException:
        elemento_span = driver.find_element(By.ID, 'lblError')
        elemento_span_text = elemento_span.text

        print(f"Usuario no existe: {elemento_span_text}")

        #await handle_websocket()

    except TimeoutException:
        # print("La tabla de afiliación no está presente en la página.")
        return None

#***************************************************
#***************************************************
#***************************************************

async def extract_names(name, last_name):
    names_list = name.split()
    surnames_list = last_name.split()

    first_name = names_list[0] if names_list else None
    middle_name = ' '.join(names_list[1:]) if len(names_list) > 1 else None
    first_surname = surnames_list[0] if surnames_list else None
    second_surname = ' '.join(surnames_list[1:]) if len(surnames_list) > 1 else None

    names_surnames_info = {
        'first_name': first_name,
        'middle_name': middle_name,
        'first_surname': first_surname,
        'second_surname': second_surname
    }


    return names_surnames_info

#***************************************************
#***************************************************
#***************************************************



















 
