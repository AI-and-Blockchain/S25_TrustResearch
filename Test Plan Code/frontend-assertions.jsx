// frontend-assertions.jsx
import { render, screen, fireEvent } from "@testing-library/react";
import App from "../App";

test("shows error when no files are selected for upload", async () => {
  render(<App />);
  const uploadBtn = screen.getByText("Upload");

  fireEvent.click(uploadBtn);
  expect(await screen.findByText(/please select files/i)).toBeInTheDocument();
});

test("shows error when review notes are empty", async () => {
  render(<App />);
  const submitBtn = screen.getByText("Submit Review Notes");

  fireEvent.click(submitBtn);
  expect(await screen.findByText(/please enter some review notes/i)).toBeInTheDocument();
});


/*
TEST PURPOSE: Frontend Validation

These tests verify that:
- Users cannot submit an upload request without selecting files
- Users cannot submit review notes if the textarea is empty
- Proper error messages are shown in each case

This ensures basic frontend integrity and user experience before triggering backend calls.
*/
