from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
#subraya porque dichas librerías no están instaladas en el sistema operativos host, pero no hay que darle importancia
#Hasta la clase pasada importabamos de django, ahora de rest frame work
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.validators import ValidationError

from e_commerce.models import Comic

#Acá van todas las vistas que representan o devuelven apis (api_view), son vistas basadas en funciones, la próxima clase vamos a ver basadas en clases

# Ahora comenzamos usando DRF:
#decorador (@) importado (ver en importaciones), funciona parecido al @app.route de flask, le pasamos un parámetro que indica el tipo de petición que acepta la view
@api_view(http_method_names=['GET'])
def comic_list_api_view(request): #es una view que representa una api que lista comics
    _queryset = Comic.objects.all() #me voy a buscar todos los comics
    _data = list(_queryset.values()) if _queryset.exists() else [] #los convierto en una lista si ese queryset existe, sino devuelvo una lista vacía
    return Response(data=_data, status=status.HTTP_200_OK) #a data le pasamos los datos que queremos que devuelva (un listado de comics)


@api_view(http_method_names=['GET'])
def comic_retrieve_api_view(request): #retrieve es recuperar, recuperar un objeto en particular de ese listado
    print('Parámetros dinámicos', request.query_params) #ver el diccionario en la consola
    instance = get_object_or_404( #importado de django
        Comic, id=request.query_params.get('id') #pasamos como parámetros el modelo asociado y un parámetro de ese modelo (por ej, el id). Si existe el parámetro, retorna el objeto (es un diccionario, no un listado) y si no existe, genera una excepción que devuelva un 404. El id es un parámetro dinámico que va al final de la url (/?id=1), podríamos hacerlo con marvel_id
    )
    return Response(
        data=model_to_dict(instance), status=status.HTTP_200_OK
    )

@api_view(http_method_names=['POST'])
def comic_create_api_view(request): #este nombre de la view es lo que vemos en la interface con capitalize y convirtiendo los guiones en espacio
    #HTTP 405 Method Not Allowed.... signfica el método GET no está permitido y también se puede ver en consola
    #en request.data obtenemos el JSON que envía el cliente, y como es un diccionario le puedo hacer .pop para que saque la clave 'marvel_id' y a ese valor lo guardo en una variable
    _marvel_id = request.data.pop('marvel_id', None)
    print(request.data) #muestra todas las claves menos 'marvel_id' (en consola)
    if not _marvel_id: #si _marvel_id es nulo (no me lo pasaste), generá una validación de error
        raise ValidationError(
            {"marvel_id": "Este campo no puede ser nulo."}
        )
    #si existe, devolvemelo
    #con _instance me traigo ese comic si existe, el _created vale false y se ejecuta el último return
    _instance, _created = Comic.objects.get_or_create(
        marvel_id=_marvel_id,
        defaults=request.data
    )
    #si no existe, crealo
    #si se creó, lo que hace es convertir la instancia que creamos en un diccionario y lo retornamos con un código de estado 201
    if _created:
        return Response(
            data=model_to_dict(_instance), status=status.HTTP_201_CREATED
        )
    #si no fue creado, va a responder de esta forma
    return Response(
        data={
            "marvel_id": "Ya existe un comic con ese valor, debe ser único."
        },
        status=status.HTTP_400_BAD_REQUEST
    )
    
@api_view(http_method_names=['GET'])
def comic_list_filtered_api_view(request):
    _queryset = Comic.objects.all().filter(price__gt=5) #me voy a buscar todos los comics con precio mayor o igual que 5
    _data = list(_queryset.values()) if _queryset.exists() else []
    return Response(data=_data, status=status.HTTP_200_OK)

@api_view(http_method_names=['GET'])
def comic_list_lowest_price_api_view(request):
    _queryset = Comic.objects.all().order_by('price')
    _data = list(_queryset.values()) if _queryset.exists() else []
    return Response(data=_data, status=status.HTTP_200_OK)

@api_view(http_method_names=['GET'])
def comic_list_highest_price_api_view(request):
    _queryset = Comic.objects.all().order_by('-price')
    _data = list(_queryset.values()) if _queryset.exists() else []
    return Response(data=_data, status=status.HTTP_200_OK)
