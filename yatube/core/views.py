from django.shortcuts import render

from http import HTTPStatus


def page_not_found(request, exception):
    return render(request, 'core/404.html', {'path': request.path},
                  status=404)

# def page_not_found(request, exception):
#     return render(request, 'core/404.html', {'path': request.path},
#                   HTTPStatus.NOT_FOUND)
# Сделал так, но pytest не проходит - https://prnt.sc/PFpbD3ZcY3W8


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html')


def internal_server_error(request, *args, **argv):
    return render(request, 'core/500.html', HTTPStatus.INTERNAL_SERVER_ERROR)


def error_403(request, exception):
    return render(request, 'core/403.html', HTTPStatus.FORBIDDEN)
