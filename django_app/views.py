from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Endpoint, UserKeenonConfig
import json
import requests
from datetime import timedelta
from django.utils import timezone

KEENON_BASE_URL = 'https://es.robotkeenon.com'


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_target_list(request):
    """
    Obtiene la lista de posiciones (targets) desde Keenon API
    Endpoint: /api/open/scene/v1/target/list
    """
    try:
        try:
            keenon_config = UserKeenonConfig.objects.get(user=request.user)
        except UserKeenonConfig.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Keenon configuration not found. Please configure your Keenon API credentials.'
            }, status=200)
        
        if not keenon_config.access_token:
            return JsonResponse({
                'success': False,
                'error': 'Access token not found. Please refresh your token.'
            }, status=200)
        
        scene_code = request.GET.get('sceneCode', keenon_config.scene_code)
        
        target_url = f"{KEENON_BASE_URL}/api/open/scene/v1/target/list"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {keenon_config.access_token}'
        }
        
        params = {
            'sceneCode': scene_code
        }
        
        try:
            response = requests.get(
                target_url,
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                target_data = response.json()
                
                return JsonResponse({
                    'success': True,
                    'data': target_data.get('data', [])
                }, status=200)
            elif response.status_code == 401:
                return JsonResponse({
                    'success': False,
                    'error': 'Token expired. Please refresh the Keenon token from Dashboard.',
                    'details': response.text,
                    'status_code': 401
                }, status=200)
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Keenon API returned status {response.status_code}',
                    'details': response.text
                }, status=200)
                
        except requests.exceptions.RequestException as e:
            return JsonResponse({
                'success': False,
                'error': 'Connection error with Keenon API',
                'details': str(e)
            }, status=200)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def call_robot_task(request):
    """
    Llama al robot de Keenon para enviar una tarea a un punto específico
    Recibe: {"uuid": "d3b7a3c371d51206d24755f9f2a80f62", "pointId": "4"}
    """
    try:
        data = request.data
        
        if 'uuid' not in data or 'pointId' not in data:
            return JsonResponse({
                'error': 'uuid and pointId are required'
            }, status=400)
        
        uuid = data['uuid']
        point_id = data['pointId']
        
        try:
            keenon_config = UserKeenonConfig.objects.get(user=request.user)
        except UserKeenonConfig.DoesNotExist:
            return JsonResponse({
                'error': 'Keenon configuration not found. Please configure your Keenon API credentials.'
            }, status=404)

        if not keenon_config.access_token:
            return JsonResponse({
                'error': 'Access token not found. Please refresh your token.'
            }, status=401)
        
        keenon_payload = {
            "uuid": uuid,
            "pointId": point_id,
            "storeId": keenon_config.store_id
        }
        
        keenon_url = "https://es.robotkeenon.com/api/open/scene/v3/robot/call/task"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {keenon_config.access_token}'
        }
        
        try:
            response = requests.post(
                keenon_url,
                json=keenon_payload,
                headers=headers,
                timeout=30
            )
            
            is_success = response.status_code in [200, 201]
            status_code = response.status_code
            
            status_messages = {
                200: 'Éxito',
                201: 'Creado',
                400: 'Petición incorrecta',
                401: 'No autorizado',
                403: 'Prohibido',
                404: 'No encontrado',
                500: 'Error del servidor',
                502: 'Bad Gateway',
                503: 'Servicio no disponible'
            }
            status_message = status_messages.get(status_code, f'Código {status_code}')
            
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            return JsonResponse({
                'success': is_success,
                'status_code': status_code,
                'status_message': status_message,
                'target': {
                    'uuid': uuid,
                    'pointId': point_id
                },
                'keenon_response': response_data
            }, status=200)
            
        except requests.exceptions.RequestException as e:
            return JsonResponse({
                'success': False,
                'error': 'Error de conexión con Keenon',
                'details': str(e)
            }, status=200)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_token(request):
    """
    Refresh the OAuth access token from Keenon API using user's credentials
    """
    try:
        try:
            keenon_config = UserKeenonConfig.objects.get(user=request.user)
        except UserKeenonConfig.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Keenon configuration not found. Please configure your Keenon API credentials.'
            }, status=404)
        
        if not keenon_config.client_id or not keenon_config.client_secret:
            return JsonResponse({
                'success': False,
                'error': 'Client ID or Client Secret not configured'
            }, status=400)
        
        token_url = "https://es.robotkeenon.com/api/open/oauth/token"
        
        token_data = {
            'client_id': keenon_config.client_id,
            'client_secret': keenon_config.client_secret,
            'grant_type': 'client_credentials'
        }
        
        token_headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(
            token_url,
            data=token_data,
            headers=token_headers,
            timeout=30
        )
        
        if response.status_code == 200:
            response_data = response.json()
            
            if 'access_token' in response_data:
                keenon_config.access_token = response_data['access_token']
                
                expires_in = response_data.get('expires_in', 3600)
                keenon_config.token_expires_at = timezone.now() + timedelta(seconds=expires_in)
                keenon_config.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Token refreshed successfully',
                    'expires_in': expires_in
                }, status=200)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No access_token in response',
                    'response': response_data
                }, status=400)
        else:
            return JsonResponse({
                'success': False,
                'error': f'Failed to refresh token (Status: {response.status_code})',
                'response': response.text
            }, status=response.status_code)
            
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'success': False,
            'error': 'Connection error',
            'details': str(e)
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def endpoint_list(request):
    """List all saved endpoints for the current user"""
    endpoints = Endpoint.objects.filter(user=request.user).values()
    return JsonResponse(list(endpoints), safe=False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def endpoint_create(request):
    """Create a new endpoint for the current user"""
    try:
        data = request.data
        
        endpoint = Endpoint.objects.create(
            user=request.user,
            name=data.get('name', 'Unnamed'),
            method=data.get('method', 'GET'),
            path=data.get('path', ''),
            params=data.get('params', ''),
            body=data.get('body', '')
        )
        
        return JsonResponse({
            'success': True,
            'endpoint': {
                'id': endpoint.id,
                'name': endpoint.name,
                'method': endpoint.method,
                'path': endpoint.path,
                'params': endpoint.params,
                'body': endpoint.body
            }
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def endpoint_update(request, endpoint_id):
    """Update an existing endpoint owned by the current user"""
    try:
        endpoint = Endpoint.objects.get(id=endpoint_id, user=request.user)
        data = request.data
        
        endpoint.name = data.get('name', endpoint.name)
        endpoint.method = data.get('method', endpoint.method)
        endpoint.path = data.get('path', endpoint.path)
        endpoint.params = data.get('params', endpoint.params)
        endpoint.body = data.get('body', endpoint.body)
        endpoint.save()
        
        return JsonResponse({
            'success': True,
            'endpoint': {
                'id': endpoint.id,
                'name': endpoint.name,
                'method': endpoint.method,
                'path': endpoint.path,
                'params': endpoint.params,
                'body': endpoint.body
            }
        }, status=200)
    except Endpoint.DoesNotExist:
        return JsonResponse({'error': 'Endpoint not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def endpoint_execute(request, endpoint_id):
    """Execute a saved endpoint owned by the current user"""
    try:
        try:
            keenon_config = UserKeenonConfig.objects.get(user=request.user)
        except UserKeenonConfig.DoesNotExist:
            return JsonResponse({
                'error': 'Keenon configuration not found. Please configure your Keenon API credentials.'
            }, status=404)
        
        if not keenon_config.access_token:
            return JsonResponse({
                'error': 'Access token not found. Please refresh your token.'
            }, status=401)
        
        endpoint = Endpoint.objects.get(id=endpoint_id, user=request.user)
        
        full_url = f"{KEENON_BASE_URL}{endpoint.path}"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {keenon_config.access_token}'
        }
        
        params_dict = {}
        if endpoint.params:
            try:
                params_dict = json.loads(endpoint.params)
            except:
                pass
        
        body_dict = None
        if endpoint.body:
            try:
                body_dict = json.loads(endpoint.body)
            except:
                pass
        
        if endpoint.method == 'GET':
            response = requests.get(full_url, headers=headers, params=params_dict, timeout=30)
        elif endpoint.method == 'POST':
            response = requests.post(full_url, headers=headers, json=body_dict, params=params_dict, timeout=30)
        elif endpoint.method == 'PUT':
            response = requests.put(full_url, headers=headers, json=body_dict, params=params_dict, timeout=30)
        elif endpoint.method == 'DELETE':
            response = requests.delete(full_url, headers=headers, params=params_dict, timeout=30)
        else:
            return JsonResponse({'error': 'Invalid method'}, status=400)
        
        try:
            response_data = response.json()
        except:
            response_data = response.text
        
        return JsonResponse({
            'success': True,
            'status_code': response.status_code,
            'response': response_data,
            'endpoint': {
                'name': endpoint.name,
                'method': endpoint.method,
                'path': endpoint.path
            }
        }, status=200)
        
    except Endpoint.DoesNotExist:
        return JsonResponse({'error': 'Endpoint not found'}, status=404)
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'error': 'Request failed',
            'details': str(e)
        }, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_robot_list(request):
    """
    Get robot list from Keenon API using user's credentials
    Endpoint: /api/open/data/v1/store/robot/list
    """
    try:
        try:
            keenon_config = UserKeenonConfig.objects.get(user=request.user)
        except UserKeenonConfig.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Keenon configuration not found. Please configure your Keenon API credentials.'
            }, status=200)
        
        if not keenon_config.access_token:
            return JsonResponse({
                'success': False,
                'error': 'Access token not found. Please refresh your token.'
            }, status=200)
        
        robot_url = f"{KEENON_BASE_URL}/api/open/data/v1/store/robot/list"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {keenon_config.access_token}'
        }
        
        params = {
            'storeId': keenon_config.store_id
        }
        
        try:
            response = requests.get(
                robot_url,
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                robot_data = response.json()
                
                return JsonResponse({
                    'success': True,
                    'data': robot_data.get('data', [])
                }, status=200)
            elif response.status_code == 401:
                return JsonResponse({
                    'success': False,
                    'error': 'Token expired. Please refresh the Keenon token from Dashboard.',
                    'details': response.text,
                    'status_code': 401
                }, status=200)
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Keenon API returned status {response.status_code}',
                    'details': response.text
                }, status=200)
                
        except requests.exceptions.RequestException as e:
            return JsonResponse({
                'success': False,
                'error': 'Connection error with Keenon API',
                'details': str(e)
            }, status=200)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_keenon_config(request):
    """Get current user's Keenon API configuration"""
    try:
        keenon_config = UserKeenonConfig.objects.get(user=request.user)
        return JsonResponse({
            'success': True,
            'config': {
                'client_id': keenon_config.client_id,
                'store_id': keenon_config.store_id,
                'scene_code': keenon_config.scene_code,
                'has_token': bool(keenon_config.access_token),
                'token_valid': keenon_config.is_token_valid(),
                'token_expires_at': keenon_config.token_expires_at.isoformat() if keenon_config.token_expires_at else None
            }
        }, status=200)
    except UserKeenonConfig.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Keenon configuration not found'
        }, status=404)


@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def update_keenon_config(request):
    """Create or update current user's Keenon API configuration"""
    try:
        data = request.data
        
        required_fields = ['client_id', 'client_secret', 'store_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({
                    'error': f'{field} is required'
                }, status=400)
        
        keenon_config, created = UserKeenonConfig.objects.get_or_create(
            user=request.user,
            defaults={
                'client_id': data['client_id'],
                'client_secret': data['client_secret'],
                'store_id': data['store_id'],
                'scene_code': data.get('scene_code', 'HU29fr')
            }
        )
        
        if not created:
            keenon_config.client_id = data['client_id']
            keenon_config.client_secret = data['client_secret']
            keenon_config.store_id = data['store_id']
            if 'scene_code' in data:
                keenon_config.scene_code = data['scene_code']
            keenon_config.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Keenon configuration saved successfully' if created else 'Keenon configuration updated successfully',
            'config': {
                'client_id': keenon_config.client_id,
                'store_id': keenon_config.store_id,
                'scene_code': keenon_config.scene_code
            }
        }, status=201 if created else 200)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_store_list(request):
    """
    Get store list from Keenon API using user's credentials
    Endpoint: /api/open/data/v1/store/list
    """
    try:
        try:
            keenon_config = UserKeenonConfig.objects.get(user=request.user)
        except UserKeenonConfig.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Keenon configuration not found. Please configure your Keenon API credentials.'
            }, status=200)
        
        if not keenon_config.access_token:
            return JsonResponse({
                'success': False,
                'error': 'Access token not found. Please refresh your token.'
            }, status=200)
        
        store_url = f"{KEENON_BASE_URL}/api/open/data/v1/store/list"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {keenon_config.access_token}'
        }
        
        try:
            response = requests.get(
                store_url,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                store_data = response.json()
                
                return JsonResponse({
                    'success': True,
                    'data': store_data.get('data', [])
                }, status=200)
            elif response.status_code == 401:
                return JsonResponse({
                    'success': False,
                    'error': 'Token expired. Please refresh the Keenon token from Dashboard.',
                    'details': response.text,
                    'status_code': 401
                }, status=200)
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Keenon API returned status {response.status_code}',
                    'details': response.text
                }, status=200)
                
        except requests.exceptions.RequestException as e:
            return JsonResponse({
                'success': False,
                'error': 'Connection error with Keenon API',
                'details': str(e)
            }, status=200)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
