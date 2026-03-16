document.getElementById('employeeForm').addEventListener('submit', function (e) {
    e.preventDefault();

    document.querySelectorAll('.error').forEach(el => el.textContent = '');
    const Employeeid = document.getElementById('Employeeid').value.trim();
    const fullName = document.getElementById('fullName').value.trim();
    const Dateofbirth = document.getElementById('Dateofbirth').value.trim();
    const email = document.getElementById('email').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const department = document.getElementById('department').value;
    const designation = document.getElementById('designation').value.trim();
    const joiningDate = document.getElementById('joiningDate').value;
    const status = document.getElementById('status').value;
    const salery = document.getElementById('salery').value;

    

    let isValid = true;
 
    if (Employeeid === "") {
        document.getElementById('EmployeeidError').textContent = "Employee ID is required.";
        isValid = false;
      }
      if (fullName === "") {
        document.getElementById('fullNameError').textContent = "Full name is required.";
        isValid = false;
      }
      if (fullName === "") {
        document.getElementById('DateofbirthError').textContent = "Date of birth is required.";
        isValid = false;
      }
    if (email === "") {
      document.getElementById('emailError').textContent = "Email is required.";
      isValid = false;
    } else if (!/^\S+@\S+\.\S+$/.test(email)) {
      document.getElementById('emailError').textContent = "Enter a valid email address.";
      isValid = false;
    }

    if (phone !== "" && !/^\d{10,15}$/.test(phone)) {
      document.getElementById('phoneError').textContent = "Enter a valid phone number.";
      isValid = false;
    }

    if (department === "") {
      document.getElementById('departmentError').textContent = "Please select a department.";
      isValid = false;
    }

    if (designation === "") {
      document.getElementById('designationError').textContent = "Designation is required.";
      isValid = false;
    }

    if (joiningDate === "") {
      document.getElementById('joiningDateError').textContent = "Joining date is required.";
      isValid = false;
    }

    if (status === "") {
      document.getElementById('statusError').textContent = "Please select an employment status.";
      isValid = false;
    }
    if (status === "") {
        document.getElementById('saleryError').textContent = "Please Enter the salery OF The Employee";
        isValid = false;
      }
    
    if (isValid) {
      alert("Employee added successfully!");
     
    }
  });