import React, { useState } from "react";
import Modal from "react-bootstrap/Modal";

export default function RetireModal() {
  const [show, setShow] = useState(false);

  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  return (
      <div>
      <button variant="primary" onClick={handleShow()}>
      Launch demo modal
      </button>

      <Modal show={show} onHide={handleClose}>
        <Modal.Header closeButton>
          <Modal.Title>Retirement Confirmation</Modal.Title>
        </Modal.Header>
          <Modal.Body>
            <label htmlFor="retirementDate">Retirement Date:</label>
            <input type="date" name="retirementDate" id="retirementDate" /><br />
            <label htmlFor="reason">Reason for Retirement:</label>
            <input type="text" id="reason" name="reason" /><br />
            <input type="checkbox" id="death" name="death" value="dead" />
            <label htmlFor="death">Dead?</label><br />
            <input type="checkbox" id="vacancy" name="vacancy" value="vacant" />
            <label htmlFor="vacancy">Did they leave a vacancy?</label><br />
          </Modal.Body>
          <Modal.Footer>
            <button className="button" onClick={handleClose}>
              Cancel
            </button>
            <button className="button button--primary" onClick={handleClose} name="submit">
              Save Changes
            </button>
          </Modal.Footer>
      </Modal>;
      </div>
    );
}
