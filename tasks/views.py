from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required


# Create your views here.
def home(request):
    return render(request, 'home.html', {})

def signup(request):
    if request.method == 'GET':
        context = {
            'form': UserCreationForm
        }
        return render(request, 'signup.html', context)

    elif request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:

            try:
                # register user
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            
            #except IntrityError:
            except Exception as e:
                mensaje_error = str(e)
                print(mensaje_error)
                error = 'Error al intentar crear l usuario, vuelva a intentar'
                
                if "UNIQUE constraint failed" in mensaje_error:
                    error = 'El usuario ya existe.'
                    
                context = {
                    'form': UserCreationForm,
                    'error': error
                }
                return render(request, 'signup.html', context)
        else:
            context = {
                'form': UserCreationForm,
                'error': 'Las contraseñas no coinciden'
            }
            return render(request, 'signup.html', context)
    else:
        context = {
            'form': UserCreationForm,
            'error': 'Método no implementado'
        }
        return render(request, 'signup.html', context)

@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, date_completed__isnull=True) 
    
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, date_completed__isnull=False).order_by('-date_completed')
    
    return render(request, 'tasks_completed.html', {'tasks': tasks})

@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {'form': TaskForm()})
    
    elif request.method == 'POST':
        try:
            form = TaskForm(request.POST)
            if form.is_valid():
                new_task = form.save(commit=False)
                new_task.user = request.user
                new_task.save()
                print(new_task)
                return redirect('tasks')
            else:
                return render(request, 'create_task.html', {'form': form})
        except Exception as e:
            print(e)
            context = {
                'form': TaskForm(request.POST),
                'error': 'Por favor, proporciona datos válidos'
            }
            return render(request, 'create_task.html', context)
    
    else:
        context = {
            'form': TaskForm(),
            'error': 'Método no implementado'
        }
        return render(request, 'create_task.html', context)

@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    form = AuthenticationForm
    if request.method == 'GET':
        context = {
            'form': form
        }
        return render(request, 'signin.html', context)
    elif request.method == 'POST':
        
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        
        if user is None:
            context = {
            'form': form,
            'error': 'usuario o contraseña inválidos'
            }
            return render(request, 'signin.html', context)
        else:
            login(request, user)
            return redirect('tasks')
    else: 
        context = {
            'form': form,
            'error': 'Método no implementado'
        }
        return render(request, 'signin.html', context)

@login_required
def task_detail(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)

    if request.method == 'GET':
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})

    elif request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('tasks')
        else:
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': 'Revise los datos del formulario.'})

    else:
        return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': 'Método no permitido.'})

@login_required
def complete_task(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    if request.method == 'POST':
        task.date_completed = timezone.now()
        task.save()
        return redirect('tasks')

@login_required   
def delete_task(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')