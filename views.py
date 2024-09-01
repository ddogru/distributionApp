import json

import googlemaps
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Package, Vehicle, Area, AreaPackageAssignment, TemporarySelection

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect

# Initialize the Google Maps client
gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)


def index(request):
    return render(request, 'index.html')


def package_table(request):
    packages = Package.objects.all()
    return render(request, 'package-table.html', {'packages': packages})


def vehicle_table(request):
    vehicles = Vehicle.objects.all()
    return render(request, 'vehicle-table.html', {'vehicles': vehicles})


def area_table(request):
    areas = Area.objects.all()
    return render(request, 'area-table.html', {'areas': areas})


import json
from django.shortcuts import render, redirect
from .models import Vehicle, Package

from django.shortcuts import render, redirect
from .models import Vehicle, Package, TemporaryPackageAssignment

def assign_packages(request):
    # Check for any temporary selections
    temp_selection = TemporarySelection.objects.first()  # Assuming only one record for simplicity
    context = {}

    if temp_selection:
        context['selected_vehicle'] = temp_selection.vehicle.id
        context['selected_package'] = temp_selection.package.id

        # After loading the temporary data, delete it
        temp_selection.delete()

    vehicles = Vehicle.objects.all()
    packages = Package.objects.filter(is_delivered=False)

    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle_id')
        package_ids = request.POST.getlist('package_id[]')

        # Save selected vehicle and packages in the session for use in Step 2
        request.session['vehicle_id'] = vehicle_id
        request.session['package_ids'] = package_ids

        area1_packages_json = request.POST.get('area1_packages', '[]')
        area2_packages_json = request.POST.get('area2_packages', '[]')
        area3_packages_json = request.POST.get('area3_packages', '[]')

        # Convert JSON strings to Python lists of dictionaries
        area1_packages = json.loads(area1_packages_json)
        area2_packages = json.loads(area2_packages_json)
        area3_packages = json.loads(area3_packages_json)

        # Clear any previous assignments for the selected packages
        TemporaryPackageAssignment.objects.filter(package__id__in=package_ids).delete()

        # Save the area packages into the TemporaryPackageAssignment table
        for pkg in area1_packages:
            pkg_id = pkg.get('packageId')  # Extract the package ID
            TemporaryPackageAssignment.objects.create(
                package_id=pkg_id,
                area='area1'
            )
        for pkg in area2_packages:
            pkg_id = pkg.get('packageId')  # Extract the package ID
            TemporaryPackageAssignment.objects.create(
                package_id=pkg_id,
                area='area2'
            )
        for pkg in area3_packages:
            pkg_id = pkg.get('packageId')  # Extract the package ID
            TemporaryPackageAssignment.objects.create(
                package_id=pkg_id,
                area='area3'
            )

        return redirect('assign-packages-2')

        # Include the vehicles, packages, and any context from the temporary selection
    context.update({
        'vehicles': vehicles,
        'packages': packages,
    })

    return render(request, 'assign-packages.html', context)


import json
from django.shortcuts import render, get_object_or_404
from .models import Vehicle, Package

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Vehicle, Package, Area, AreaPackageAssignment, TemporaryPackageAssignment

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from .models import Vehicle, Package, Area, AreaPackageAssignment, TemporaryPackageAssignment


def assign_packages_2(request):
    if request.method == 'POST':
        vehicle_id = request.session.get('vehicle_id')
        if not vehicle_id:
            messages.error(request, "Vehicle selection is missing.")
            return redirect('assign-packages')

        # Retrieve selected vehicle and packages from the session
        vehicle = Vehicle.objects.get(id=vehicle_id)
        area1_package_ids = request.POST.getlist('area1_package_ids[]')
        area2_package_ids = request.POST.getlist('area2_package_ids[]')
        area3_package_ids = request.POST.getlist('area3_package_ids[]')

        # Retrieve or create areas
        area1 = Area.objects.get(area_name='area1', vehicle=vehicle)
        area2 = Area.objects.get(area_name='area2', vehicle=vehicle)
        area3 = Area.objects.get(area_name='area3', vehicle=vehicle)

        AreaPackageAssignment.objects.all().delete()

        # Save AreaPackageAssignment instances
        for package_id in area1_package_ids:
            package = Package.objects.get(id=package_id)
            AreaPackageAssignment.objects.create(vehicle=vehicle, area=area1, package=package)
            package.is_delivered = True
            package.save()

        for package_id in area2_package_ids:
            package = Package.objects.get(id=package_id)
            AreaPackageAssignment.objects.create(vehicle=vehicle, area=area2, package=package)
            package.is_delivered = True
            package.save()

        for package_id in area3_package_ids:
            package = Package.objects.get(id=package_id)
            AreaPackageAssignment.objects.create(vehicle=vehicle, area=area3, package=package)
            package.is_delivered = True
            package.save()

        # Clear temporary assignments
        TemporaryPackageAssignment.objects.all().delete()

        # Generate PDF
        pdf_buffer = BytesIO()
        generate_pdf(pdf_buffer, vehicle, area1, area2, area3)
        pdf_buffer.seek(0)

        # Create HTTP response
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="assignment_summary.pdf"'
        return response

    else:
        # Retrieve vehicle and packages
        vehicle_id = request.session.get('vehicle_id')
        package_ids = request.session.get('package_ids', [])

        vehicle = Vehicle.objects.get(id=vehicle_id)
        packages = Package.objects.filter(id__in=package_ids)

        # Prepare context
        temp_areas1 = TemporaryPackageAssignment.objects.filter(area='area1')
        temp_areas2 = TemporaryPackageAssignment.objects.filter(area='area2')
        temp_areas3 = TemporaryPackageAssignment.objects.filter(area='area3')

        area1_package_ids = temp_areas1.values_list('package_id', flat=True)
        area2_package_ids = temp_areas2.values_list('package_id', flat=True)
        area3_package_ids = temp_areas3.values_list('package_id', flat=True)

        context = {
            'vehicle': vehicle,
            'packages': packages,
            'area1_package_ids': list(area1_package_ids),
            'area2_package_ids': list(area2_package_ids),
            'area3_package_ids': list(area3_package_ids),
        }
        return render(request, 'assign-packages-2.html', context)


def generate_pdf(buffer, vehicle, area1, area2, area3):
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.drawString(100, height - 100, f"Vehicle: {vehicle.vehicle_name}")
    c.drawString(100, height - 120, f"Weight Capacity: {vehicle.weight_capacity} kg")
    c.drawString(100, height - 140, f"Size Capacity: {vehicle.size_capacity} m³")

    c.drawString(100, height - 180, "Area Assignments:")

    y_position = height - 220
    for area, area_name in [(area1, 'Area 1'), (area2, 'Area 2'), (area3, 'Area 3')]:
        c.drawString(100, y_position, f"{area_name}:")
        y_position -= 20

        packages = AreaPackageAssignment.objects.filter(area=area).values_list('package__package_name', flat=True)
        for package in packages:
            c.drawString(120, y_position, package)
            y_position -= 20

        y_position -= 20  # Add extra space between areas

    c.showPage()
    c.save()


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from .models import Vehicle, Package, TemporarySelection

@csrf_exempt
def save_temporary_selection(request):
    # Clear the entire TemporarySelection table
    TemporarySelection.objects.all().delete()
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received data:", data)  # Debugging line

            vehicle_id = data.get('vehicle_id')
            package_id = data.get('package_id')

            # Check if IDs are present
            if vehicle_id is None or package_id is None:
                return JsonResponse({'error': 'Vehicle ID or Package ID missing.'}, status=400)

            # Convert IDs to integers
            try:
                vehicle_id = int(vehicle_id)
                package_id = int(package_id)
            except ValueError:
                return JsonResponse({'error': 'Invalid ID format.'}, status=400)

            # Fetch Vehicle and Package objects
            vehicle = get_object_or_404(Vehicle, id=vehicle_id)
            package = get_object_or_404(Package, id=package_id)



            # Create TemporarySelection record
            TemporarySelection.objects.create(vehicle=vehicle, package=package)
            temp_object = TemporarySelection.objects.get(vehicle=vehicle, package=package)
            print('temp object', temp_object)

            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except Exception as e:
            print("Error:", str(e))  # Debugging line
            return JsonResponse({'error': 'Server error.'}, status=500)

    return JsonResponse({'status': 'fail'}, status=400)

@csrf_exempt
def add_package(request):
    if request.method == 'POST':
        package_name = request.POST.get('package_name')
        weight = request.POST.get('weight')
        size = request.POST.get('size')
        package_type = request.POST.get('type')
        package_location = request.POST.get('package_location')

        try:
            package = Package(
                package_name=package_name,
                weight=float(weight),
                size=float(size),
                package_type=package_type,
                package_location=package_location
            )
            package.save()

            return JsonResponse({'status': 'success', 'message': 'Package added successfully!'})

        except ValueError as e:

            return JsonResponse({'status': 'error', 'message': f'Error: {str(e)}'})

        except Exception as e:

            return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'})

    # For non-POST requests, render the form page
    return render(request, 'add-package.html')


@csrf_protect
def add_vehicle(request):
    if request.method == 'POST':
        vehicle_name = request.POST.get('vehicle_name')
        weight_capacity = request.POST.get('weight_capacity')
        size_capacity = request.POST.get('size_capacity')
        vehicle_type = request.POST.get('vehicle_type')
        km_capacity = request.POST.get('km_capacity')

        # Create and save the new vehicle
        vehicle = Vehicle(
            vehicle_name=vehicle_name,
            weight_capacity=weight_capacity,
            size_capacity=size_capacity,
            vehicle_type=vehicle_type,
            km_capacity=km_capacity
        )
        vehicle.save()

        # Create areas for the new vehicle
        area_choices = ['area1', 'area2', 'area3']
        for area_name in area_choices:
            Area.objects.create(
                area_name=area_name,
                vehicle=vehicle
            )

        return JsonResponse(
            {'status': 'success', 'message': 'Vehicle and associated areas have been added successfully.'})

    return render(request, 'add-vehicle.html')



