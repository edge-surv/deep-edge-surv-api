# DeepEdgeSurv API Docs using FastAPI

Base URL: `http://0.0.0.0:8000`

## Overview
This API provides functionality for managing cameras, settings, and AI-powered surveillance. Below are the available endpoints.

---

## Endpoints

### **Cameras**

#### `GET /api/cameras/`
- **Summary**: Get all cameras.
- **Responses**:
  - `200`: Successful response with a list of cameras.

#### `POST /api/cameras/`
- **Summary**: Add a new camera.
- **Request Body**:
  - **Schema**: `Camera`
    - `id` (string) - Required
    - `host` (string) - Required
    - `port` (integer) - Required
    - `name` (string) - Required
    - `username` (string) - Required
    - `password` (string) - Required
    - `provider` (string) - Required
- **Responses**:
  - `200`: Camera added successfully.
  - `422`: Validation error.

#### `DELETE /api/cameras/{camera_id}`
- **Summary**: Delete a camera.
- **Path Parameters**:
  - `camera_id` (string) - Required.
- **Responses**:
  - `200`: Camera deleted successfully.
  - `422`: Validation error.

#### `PUT /api/cameras/{camera_id}`
- **Summary**: Update a camera's information.
- **Path Parameters**:
  - `camera_id` (string) - Required.
- **Request Body**:
  - **Schema**: `Camera`
- **Responses**:
  - `200`: Camera updated successfully.
  - `422`: Validation error.

#### `GET /api/cameras/scan`
- **Summary**: Discover cameras on the network.
- **Responses**:
  - `200`: List of discovered cameras.

---

### **Surveillance**

#### `GET /api/streams/{camera_id}/surveillance`
- **Summary**: Start live AI-powered surveillance for a specific camera.
- **Path Parameters**:
  - `camera_id` (string) - Required.
- **Responses**:
  - `200`: Successful response.
  - `422`: Validation error.

---

### **Settings**

#### `GET /api/settings/`
- **Summary**: Retrieve current system settings.
- **Responses**:
  - `200`: Current settings.

#### `PUT /api/settings/`
- **Summary**: Update system settings.
- **Request Body**:
  - **Schema**: `Settings`
    - `detection_objects` (array of strings) - Required.
    - `enabled` (boolean) - Required.
    - `minimum_confidence` (integer or float) - Required.
    - `enable_tracking` (boolean) - Required.
    - `enable_counting` (boolean) - Required.
- **Responses**:
  - `200`: Settings updated successfully.
  - `422`: Validation error.

#### `POST /api/settings/`
- **Summary**: Save new settings configuration.
- **Request Body**:
  - **Schema**: `Settings`
- **Responses**:
  - `200`: Settings saved successfully.
  - `422`: Validation error.

---

## Schemas

### **Camera**
- `id` (string) - Unique identifier for the camera.
- `host` (string) - Camera host address.
- `port` (integer) - Camera port number.
- `name` (string) - Camera name.
- `username` (string) - Username for authentication.
- `password` (string) - Password for authentication.
- `provider` (string) - Camera provider.

### **Settings**
- `detection_objects` (array of strings) - Objects to detect.
- `enabled` (boolean) - Enable or disable detection.
- `minimum_confidence` (integer) - Minimum confidence threshold for detection.
- `enable_tracking` (boolean) - Enable object tracking.
- `enable_segmentation` (boolean) - Enable object segmentation.
- `enable_counting` (boolean) - Enable object counting.

### **ValidationError**
- `loc` (array of strings/integer) - Location of the error.
- `msg` (string) - Error message.
- `type` (string) - Error type.

### **HTTPValidationError**
- `detail` (array of `ValidationError`) - List of validation errors.

---

## Notes
- Ensure that all required fields are provided when adding or updating data.
- For real-time surveillance, ensure the specified `camera_id` exists in the system.
