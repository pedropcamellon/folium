from mcp.server.fastmcp import FastMCP

# Create a new instance of the FastMCP server
mcp = FastMCP("ehr_mcp_server")


@mcp.tool()
def GetPatientData(patient_id: str) -> dict:
    """
    Retrieves patient data from the EHR system.

    Args:
        patient_id (str): The ID of the patient to retrieve data for.

    Returns:
        Dict: A dictionary containing the patient's data.
    """
    # Return dummy data for now
    return {
        "resourceType": "Patient",
        "id": patient_id,
        "name": [{"family": "Doe", "given": ["John"]}],
        "telecom": [{"system": "phone", "value": "555-555-5555"}],
        "address": [
            {
                "line": ["123 Main St"],
                "city": "Anytown",
                "state": "NY",
                "postalCode": "12345",
            }
        ],
    }

    # # Construct the API request to the EHR system
    # url = f"https://ehr-system.com/api/patients/{patient_id}"
    # headers = {"Authorization": "Bearer YOUR_API_TOKEN"}
    # response = requests.get(url, headers=headers)

    # # Check if the response was successful
    # if response.status_code == 200:
    #     return response.json()
    # else:
    #     raise Exception(f"Failed to retrieve patient data: {response.text}")


# Run the FastMCP server
if __name__ == "__main__":
    mcp.run(transport="stdio")
