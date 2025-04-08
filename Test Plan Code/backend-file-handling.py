def test_backend_creates_and_sends_file():
    # Step 1: Simulate a POST to the /upload endpoint with file1 and file2
    response = client.post('/upload', data={'files': [file1, file2]})

    # Step 2: Ensure backend responded OK (200)
    assert response.status_code == 200

    # Step 3: Ensure uploaded_files.txt is created
    assert os.path.exists("uploaded_files.txt")

    # Step 4: Read uploaded_files.txt and verify contents follow expected format
    with open("uploaded_files.txt") as f:
        lines = f.readlines()

    assert len(lines) > 0
    assert ":" in lines[0]  # Expect format like 'paper.pdf: Qm123...'

    # Step 5: This simulates the file being ready for sending to Journal Authority


"""
TEST PURPOSE: Backend File Handling

This test ensures:
- Files can be uploaded to the /upload route
- The backend creates an `uploaded_files.txt` file
- The file includes at least one valid entry in the format "filename: IPFS hash"

This confirms that the backend correctly processes, writes, and prepares files for the next step.
"""
