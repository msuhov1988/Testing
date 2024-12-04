import socket
import json
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .constants import DB_SERVER_HOST, DB_SERVER_PORT, DB_META_COMMAND


_JSON_META = json.dumps(DB_META_COMMAND).encode(encoding='utf-8')


def _local_server_communicate(data: bytes):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((DB_SERVER_HOST, DB_SERVER_PORT))
            sock.send(len(data).to_bytes(4, byteorder="little"))
            sock.sendall(data)

            length = sock.recv(4)
            length, read, chunks = int.from_bytes(length, byteorder="little"), 0, []
            while read < length:
                chunk = sock.recv(1024).strip()
                chunks.append(chunk)
                read += len(chunk)
            answer = b"".join(chunks)
            return answer
    except ConnectionRefusedError:
        return [None, "Что-то пошло не так. Сервер базы данных не отвечает. Повторите попытку чуть позже"]


@require_http_methods(["GET"])
def home(request):
    return render(request, "index.html")


@require_http_methods(["GET"])
def meta(_):
    json_answer = _local_server_communicate(data=_JSON_META)
    return HttpResponse(json_answer, content_type="application/json")


@require_http_methods(["POST"])
@csrf_exempt
def period_data(request):
    data = request.body
    json_answer = _local_server_communicate(data=data)
    return HttpResponse(json_answer, content_type="application/json")
