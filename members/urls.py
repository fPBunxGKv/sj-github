from django.urls import path, include
from django.contrib import admin

from . import views

urlpatterns = [
            path('', views.index, name='index'),

            path('register/', views.register_new, name='register_new'),
            path('register/<uuid:id>/', views.register_new, name='register_new'),
            path('register/<str:id>/', views.register_string, name='register_string'),
            path('anmeldung/', views.register_new, name='register_new'),
            path('anmeldung/<uuid:id>/', views.register_new, name='register_new'),
            path('anmeldung/<str:id>/', views.register_string, name='register_string'),
            path('thankyou/', views.thankyou, name='thankyou'),

            path('users/', views.users, name='users'),
            path('users/edit/<uuid:id>', views.edit, name='edit'),
            path('users/edit/updaterecord/<uuid:id>', views.updaterecord, name='updaterecord'),
            
            path('add/', views.add, name='add'),
            path('add/addrecord/', views.addrecord, name='addrecord'),
            path('edit/addrecord/', views.addrecord, name='addrecord'),

            path('delete/<uuid:id>', views.delete, name='delete'),

            path('run/', views.run, name='run'),
            path('run/addrun/', views.addrun, name='addrun'),
            path('run/edit/<int:id>', views.editrun, name='editrun'),
            path('run/edit/updaterun/', views.updaterun, name='updaterun'),
            path('printfinal/', views.print_final_runs, name='print_final_runs'),

            path('results/' , views.results, name='results'),
            path('results/addresults/<int:id>' , views.addresults, name='addresults'),
            path('results/addresults/saveresults/' , views.saveresults, name='saveresults'),

            path('setfinal/', views.set_final_runs, name='set_final_runs'),
            path('ranking/', views.ranking, name='ranking'),
            path('addtestdata/', views.addrun_testdata, name='addtestdata'),
            path('addtestdata/<int:add_lines>', views.addrun_testdata, name='addtestdata'),

            # Login
            path('accounts/', include('django.contrib.auth.urls')),

            # Administration
            path('administration/', views.administration, name='administration'),
            ]
