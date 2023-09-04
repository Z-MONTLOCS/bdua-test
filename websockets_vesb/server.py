
from selenium.webdriver.common.by import By
import asyncio
import websockets
import json

from config_utils import (
    initialize_driver,
    set_data_query,
    get_url_captcha_image,
    set_code,
    get_new_tab,
    get_personal_data,
    get_affiliation_data,
    extract_names,
)

socket_data = {}

async def handle_client(websocket, path):
    try:
        while True:

            # Recibir información
            data = await websocket.recv()
            data_dict = json.loads(data)  
            print(f"request cliente {data}:")

#***************************************************
#***************************************************
#***************************************************

            if data_dict.get("message") == "data":

                socket_id = id(websocket)

                personal_data = {
                    'message': data_dict.get("message"),
                    'socket_id': socket_id,
                    'documentType': data_dict.get("documentType"),
                    'identificationNumber': data_dict.get("identificationNumber"),
                    'code': data_dict.get("code"),
                    'urlImage': data_dict.get("urlImage"),
                
                }

                socket_data[socket_id] = personal_data

                # print(f"Server Response data")
                # print(f"Información asociada a socket ID {socket_id}:")
                # print(socket_data[socket_id])

                socket_data[socket_id]['message'] = "data save"
                await websocket.send(json.dumps({"server_response": socket_data[socket_id]}))


            # print(f"Cliente request")
            # print(f"Información asociada a socket ID {socket_id}:")
            # print(f"mensaje {personal_data.get('message')}")

#***************************************************
#***************************************************
#***************************************************

            if  data_dict.get("message") == "resgisterForms":


                socket_data[socket_id]['message'] = "data validate"
                await websocket.send(json.dumps({"server_response": socket_data[socket_id]}))

                browser = await initialize_driver()

                # print(f"response browser {browser}:")

                if browser == "Error al cargar la página:":

                    socket_data[socket_id]['message'] = "page no fount BDUA"
                    await websocket.send(json.dumps({"server_response": socket_data[socket_id]}))
                    # print(f"result {browser}")


                elif browser == "Error al inicializar el controlador:":
                   
                    socket_data[socket_id]['message'] = "Error al inicializar el driver"
                    await websocket.send(json.dumps({"server_response": socket_data[socket_id]}))
                    # print(f"result server {browser}")

                
                     
                response = await set_data_query(browser, data_dict) 
                # print(f"response server {response}:")

                if response == "Número de Identificación No Válida.":

                            # print(f"response server {response}:")
                            socket_data[socket_id]['message'] = "error_number_input"
                            await websocket.send(json.dumps({"server_response": socket_data[socket_id]}))

                else:
                    
                            url_image = await get_url_captcha_image(browser)   
                            # print(f":imageLink: {url_image}")
                           
                            socket_data[socket_id]['urlImage'] = url_image
                            socket_data[socket_id]['message'] = "link send"
                            await websocket.send(json.dumps({"server_response": socket_data[socket_id]}))
                            # print(f"Información asociada a socket ID {socket_id}:")
                            # print(socket_data[socket_id])

#***************************************************
#***************************************************
#***************************************************

            if  data_dict.get("message") == "code send":
                socket_data[socket_id]['code'] = data_dict.get("code")
                # print("")
                # print("")
                # print(f"Información asociada a socket ID {socket_id}:")
                # print(socket_data[socket_id])
                # print("")
                # print("") 

                socket_data[socket_id]['message'] = "code validate"
                await websocket.send(json.dumps({"server_response": socket_data[socket_id]}))


                erro_input_code= await set_code(browser, data_dict)

                # print(f"Información asociada a socket ID {erro_input_code}:")

                if erro_input_code == "El codigo ingresado no es valido":

                    # print("El codigo ingresado no es valido:", erro_input_code)

                    socket_data[socket_id]['message'] = "code error"
                    await websocket.send(json.dumps({"server_response": socket_data[socket_id]}))
                else:
                    # print("codigo correcto sever:", erro_input_code)
                    socket_data[socket_id]['message'] = "charge"
                    await websocket.send(json.dumps({"server_response":socket_data[socket_id]}))

#***************************************************
#***************************************************
#***************************************************

                
            if  data_dict.get("message") == "get data":           
                        
                        await get_new_tab(browser)
                        information =await  get_personal_data(browser)
                        affiliation_info = await get_affiliation_data(browser)

                        if affiliation_info == None:
                                
                           elemento_span = browser.find_element(By.ID, 'lblError')

                        #    print("Enviar:",elemento_span.text)
                                
                           socket_data[socket_id]['message'] = "user no found"
                           socket_data[socket_id]['message_error'] = elemento_span.text
                           await websocket.send(json.dumps({"server_response": socket_data[socket_id]}))

                               
                           browser.execute_script("window.stop();")
                                #browser.quit()  

                        else:    
                                names_surnames_info = await extract_names( information['NOMBRES'], information['APELLIDOS'])
                                info = {
                                'first_name': names_surnames_info['first_name'],
                                'middle_name': names_surnames_info['middle_name'],
                                'last_name': names_surnames_info['first_surname'],
                                'second_last_name': names_surnames_info['second_surname'],
                                'eps': affiliation_info['EPS'] 
                                }  

                                socket_data[socket_id]['first_name'] = names_surnames_info['first_name']
                                socket_data[socket_id]['middle_name'] = names_surnames_info['middle_name']
                                socket_data[socket_id]['last_name'] = names_surnames_info['first_surname']
                                socket_data[socket_id]['second_last_name'] = names_surnames_info['second_surname']
                                socket_data[socket_id]['eps'] = affiliation_info['EPS'] 

                    
                                socket_data[socket_id]['message'] = "charge data"
                                await websocket.send(json.dumps({"server_response": socket_data[socket_id]}))

                                print('Información:')
                                print('Primer nombre:', info['first_name'])
                                print('Segundo nombre:', info['middle_name'])
                                print('Primer apellido:', info['last_name'])
                                print('Segundo apellido:', info['second_last_name'])
                                print('EPS:', affiliation_info['EPS'])

#***************************************************
#***************************************************
#***************************************************

    except websockets.exceptions.ConnectionClosed:
        print(f"Conexión cerrada para el ID de socket: {socket_id}")
        if socket_id in socket_data:
            del socket_data[socket_id]

#***************************************************
#***************************************************
#***************************************************


async def main():
    server = await websockets.serve(handle_client, "localhost", 8765)

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())