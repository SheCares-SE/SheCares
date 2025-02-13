# # from patient.models import Doctor
# # from patient.forms import SymptomForm
# # from patient import models
# # from patient.models import Symptom
# from .models import Doctor, Symptom
# from .forms import SymptomForm
# from django.http import JsonResponse

# def get_doctors(request):
#     symptom_name = request.GET.get("symptom", None)
#     if symptom_name:
#         related_specialization = Symptom.objects.filter(name=symptom_name).values_list("related_specialization", flat=True)
#         doctors = Doctor.objects.filter(specialization__in=related_specialization).values("name", "specialization")
#         return JsonResponse({"doctors": list(doctors)})
#     return JsonResponse({"doctors": []})



# # @login_required
# # def recommend_doctor(request):
# #     doctors = Doctor.objects.all()  # ✅ Fetch all doctors
# #     print("Doctors Retrieved:", doctors)  # ✅ Debugging output in terminal
# #     return render(request, "patient/recommend_doctor.html", {"doctors": doctors})

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from .models import Doctor, Symptom
# @login_required
# def recommend_doctor(request):
#     symptoms = Symptom.objects.all()  # Fetch all symptoms for dropdown
#     doctors = None  

#     if request.method == "POST":
#         selected_symptom = request.POST.get("symptom")  # Get selected symptom
#         if selected_symptom:
#             # Get the related specialization for the selected symptom
#             related_specializations = Symptom.objects.filter(name=selected_symptom).values_list("related_specialization", flat=True)

#             if related_specializations:
#                 # Get doctors with matching specializations
#                 doctors = Doctor.objects.filter(specialization__in=related_specializations)

#     return render(request, "patient/recommend_doctor.html", {"doctors": doctors, "symptoms": symptoms})


# @login_required
# def form_page(request):
#     doctors = Doctor.objects.all()  # Fetch all doctors from DB
#     print(doctors)
#     return render(request, "patient/recommend_doctor.html", {'doctors': doctors})

# def some_view(request):
#     from .models import Symptom  # Import inside the function
#     symptoms = Symptom.objects.all()
#     return render(request, "template.html", {"symptoms": symptoms})
from django.shortcuts import render , redirect
from django.contrib.auth.decorators import login_required
from gync.models import Appointment, Availability
from gync.forms import AppointmentRequestForm

@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentRequestForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.status = 'Pending'
            appointment.save()
            return redirect('/appointments/')
    else:
        form = AppointmentRequestForm()
    
    return render(request, 'patient/book_appointment.html', {'form': form})

@login_required
def patient_appointments(request):
    appointments = Appointment.objects.filter(patient=request.user)
    return render(request, 'patient/patient_appointments.html', {'appointments': appointments})
@login_required
def patient_dashboard(request):
    return render(request, 'patient_dashboard.html')