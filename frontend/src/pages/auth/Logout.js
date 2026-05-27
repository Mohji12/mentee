import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { API_BASE_URL } from "../../api";
import '../../assets/css/Logout.css';

const Logout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [showModal, setShowModal] = useState(true);
  const [message, setMessage] = useState("Are you sure you want to log out?");

  const from = location.state?.from;

  const handleConfirmLogout = async () => {
    setMessage("Byeee! Logging out now...");

    const token = sessionStorage.getItem("access_token");
    const userId = sessionStorage.getItem("userId");

    if (!token || !userId) {
      navigate("/"); // Fallback if session is broken
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/auth/logout/${userId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        sessionStorage.clear();
        setTimeout(() => {
          navigate("/login");
        }, 1500);
      } else {
        setMessage("Logout failed. Try again.");
      }
    } catch (err) {
      setMessage("An error occurred. Please try again.");
    }
  };

  return (
    showModal && (
      <div className="modal">
        <div className="modal-content">
          <p>{message}</p>
          {message === "Are you sure you want to log out?" && (
            <>
              <button className="newbutton" onClick={handleConfirmLogout}>Yes</button>
              {from ? (
                <button className="newbutton" onClick={() => navigate(from)}>No</button>
              ) : (
                <button className="newbutton" onClick={() => setShowModal(false)}>No</button>
              )}
            </>
          )}
        </div>
      </div>
    )
  );
};

export default Logout;
