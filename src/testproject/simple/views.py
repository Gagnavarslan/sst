import os
import signal

from django.shortcuts import render_to_response


def index(request):
    response = render_to_response('index.html', {'title': 'The Page Title'})
    response.set_cookie('foo', 'bar')
    response.set_cookie('baz', 'qux')
    return response


def begin(request):
    return render_to_response('begin.html', {'title': 'The Next Page'})


def longscroll(request):
    return render_to_response('longscroll.html', {'title': 'Long Scroll Page'})


def nojs(request):
    return render_to_response('nojs.html', {'title': 'No JavaScript Test'})


def html5(request):
    return render_to_response('html5.html')


def popup(request):
    return render_to_response('popup_with_frame.html',
                              {'title': 'Popup Window'})


def frame_a(request):
    return render_to_response('frame_a.html')


def frame_b(request):
    return render_to_response('frame_b.html')


def alerts(request):
    return render_to_response('alerts.html')


def yui(request):
    return render_to_response('yui.html')


def tables(request):
    return render_to_response('tables.html')


def page_to_save(request):
    return render_to_response('page_to_save.html')


def kill_django(request):
    os.kill(os.getpid(), signal.SIGKILL)
