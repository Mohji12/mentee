import React, { useState, useEffect, useRef, useCallback } from "react";
import { useParams } from "react-router-dom";
import jsQR from "jsqr";
import { FaCamera, FaSyncAlt, FaStop, FaQrcode } from "react-icons/fa";
import "../../../assets/css/Attendance.css";
import { API_BASE_URL } from "../../../api";

const Attendance = () => {
  const { student_usn } = useParams();
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [facingMode, setFacingMode] = useState("environment");
  const [dashboardStats, setDashboardStats] = useState(null);

  // Refs for video and stream management
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const canvasRef = useRef(null);
  const scanIntervalRef = useRef(null);
  const isMountedRef = useRef(true);
  const isProcessingRef = useRef(false);
  const lastScannedSessionIdRef = useRef(null);
  const scanTimeoutRef = useRef(null);
  const handleQRCodeScanRef = useRef(null);

  // Fetch attendance records
  const fetchAttendanceRecords = useCallback(async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/student/${student_usn}/attendance/my-records`
      );
      if (response.ok) {
        const data = await response.json();
        setAttendanceRecords(data || []);
      }
    } catch (err) {
      console.error("Error fetching attendance records:", err);
    }
  }, [student_usn]);

  const fetchStats = useCallback(async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/student/${student_usn}/attendance/stats`
      );
      if (response.ok) {
        const data = await response.json();
        setDashboardStats(data);
      }
    } catch (err) {
      console.error("Error fetching attendance stats:", err);
    }
  }, [student_usn]);

  useEffect(() => {
    fetchAttendanceRecords();
    fetchStats();
  }, [fetchAttendanceRecords, fetchStats]);

  // Start camera and QR scanning
  useEffect(() => {
    if (!scanning || !isMountedRef.current) return;

    let isCancelled = false;
    const currentVideo = videoRef.current;
    const currentCanvas = canvasRef.current;

    const startCamera = async () => {
      try {
        if (!currentVideo || isCancelled) return;

        // Prevent multiple camera loads
        if (streamRef.current) {
          return;
        }

        // Get user media
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { 
            facingMode: facingMode,
            width: { ideal: 1280 },
            height: { ideal: 720 }
          }
        });

        if (!isMountedRef.current || isCancelled) {
          stream.getTracks().forEach(track => track.stop());
          return;
        }

        streamRef.current = stream;
        currentVideo.srcObject = stream;
        
        // Play video
        await currentVideo.play().catch(() => {
          // Ignore play errors
        });

        if (!isMountedRef.current || isCancelled) return;

        // Start QR code scanning
        startQRScanning();

      } catch (err) {
        console.error("Camera start error:", err);
        if (isMountedRef.current && !isCancelled) {
          setError("Failed to start camera. Please check permissions and try again.");
          setScanning(false);
        }
      }
    };

    const startQRScanning = () => {
      if (!currentVideo || !currentCanvas || isCancelled) return;

      const video = currentVideo;
      const canvas = currentCanvas;
      const context = canvas.getContext("2d", { willReadFrequently: true });

      const scan = () => {
        if (!video || !canvas || !context || isCancelled || !isMountedRef.current) {
          return;
        }

        if (video.readyState === video.HAVE_ENOUGH_DATA) {
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          context.drawImage(video, 0, 0, canvas.width, canvas.height);
          
          const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
          const code = jsQR(imageData.data, imageData.width, imageData.height);

          if (code && !isProcessingRef.current) {
            // QR code detected - use the latest handleQRCodeScan from ref
            const currentHandleQR = handleQRCodeScanRef.current;
            if (currentHandleQR) {
              currentHandleQR(code.data);
            }
          }
        }

        if (!isCancelled && isMountedRef.current) {
          scanIntervalRef.current = requestAnimationFrame(scan);
        }
      };

      scan();
    };

    startCamera();

    return () => {
      isCancelled = true;
      
      // Stop scanning
      if (scanIntervalRef.current) {
        cancelAnimationFrame(scanIntervalRef.current);
        scanIntervalRef.current = null;
      }

      // Stop video stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }

      // Clear video source using the captured ref
      if (currentVideo) {
        currentVideo.srcObject = null;
      }
    };
  }, [scanning, facingMode]);

  // Component mount tracking
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
      
      // Clear timeouts
      if (scanTimeoutRef.current) {
        clearTimeout(scanTimeoutRef.current);
      }
      
      // Stop stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
    };
  }, []);

  const startScanner = () => {
    setError("");
    setSuccess("");
    setScanning(true);
  };

  const stopScanner = useCallback(async () => {
    // Stop scanning
    if (scanIntervalRef.current) {
      cancelAnimationFrame(scanIntervalRef.current);
      scanIntervalRef.current = null;
    }

    // Clear timeout
    if (scanTimeoutRef.current) {
      clearTimeout(scanTimeoutRef.current);
      scanTimeoutRef.current = null;
    }

    // Reset flags
    isProcessingRef.current = false;
    lastScannedSessionIdRef.current = null;

    // Stop video stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    // Clear video source
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    // Wait a bit before removing from DOM
    await new Promise(resolve => setTimeout(resolve, 200));

    setScanning(false);
  }, []);

  const switchCamera = async () => {
    if (!scanning || loading) return;

    try {
      // Stop current stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }

      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }

      // Stop scanning
      if (scanIntervalRef.current) {
        cancelAnimationFrame(scanIntervalRef.current);
        scanIntervalRef.current = null;
      }

      // Wait before switching
      await new Promise(resolve => setTimeout(resolve, 300));

      // Toggle facing mode
      const newFacingMode = facingMode === "environment" ? "user" : "environment";
      setFacingMode(newFacingMode);

      // Wait before restart
      await new Promise(resolve => setTimeout(resolve, 200));
      
    } catch (err) {
      console.error("Error switching camera:", err);
      setError("Failed to switch camera. Please try again.");
    }
  };

  const handleQRCodeScan = useCallback(async (qrData) => {
    if (loading || isProcessingRef.current) return;

    // Clear timeout
    if (scanTimeoutRef.current) {
      clearTimeout(scanTimeoutRef.current);
    }

    // Debounce
    scanTimeoutRef.current = setTimeout(async () => {
      if (isProcessingRef.current || loading) return;

      try {
        isProcessingRef.current = true;
        setLoading(true);

        // Stop scanning temporarily
        if (scanIntervalRef.current) {
          cancelAnimationFrame(scanIntervalRef.current);
          scanIntervalRef.current = null;
        }

        // Parse QR code
        let qrDataObj;
        try {
          qrDataObj = JSON.parse(qrData);
        } catch (parseError) {
          throw new Error("Invalid QR code format. Please scan a valid attendance QR code.");
        }

        const sessionId = qrDataObj.session_id;
        if (!sessionId) {
          throw new Error("Invalid QR code format. Missing session ID.");
        }

        // Check for duplicate scan
        if (lastScannedSessionIdRef.current === sessionId) {
          await fetchAttendanceRecords();
          isProcessingRef.current = false;
          setLoading(false);
          return;
        }

        // Check session validity
        const checkResponse = await fetch(
          `${API_BASE_URL}/student/${student_usn}/attendance/check-session/${sessionId}`,
          {
            method: "GET",
            headers: { "Content-Type": "application/json" },
          }
        );

        if (!checkResponse.ok) {
          if (checkResponse.status === 404) {
            throw new Error("Student not found. Please contact support.");
          }
          const errorData = await checkResponse.json().catch(() => ({}));
          throw new Error(errorData.detail || "Failed to check session validity");
        }

        const checkData = await checkResponse.json();

        if (!checkData.valid) {
          throw new Error(checkData.message || "Session is not valid or has expired");
        }

        if (checkData.already_marked) {
          setError("You have already marked attendance for this session");
          setTimeout(() => setError(""), 5000);
          isProcessingRef.current = false;
          setLoading(false);
          return;
        }

        // Mark attendance
        const response = await fetch(
          `${API_BASE_URL}/student/${student_usn}/attendance/scan-qr`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              session_id: sessionId,
              student_usn: student_usn,
            }),
          }
        );

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          let errorMessage = errorData.detail || "Failed to mark attendance";
          
          if (response.status === 400 && errorMessage.includes("already marked")) {
            errorMessage = "You have already marked attendance for this session";
            lastScannedSessionIdRef.current = null;
          } else if (response.status === 404) {
            errorMessage = "Session not found. The QR code may be invalid.";
          } else if (response.status === 403) {
            errorMessage = "Unauthorized. Please ensure you're logged in correctly.";
          } else if (response.status === 500) {
            errorMessage = errorData.detail || "Server error. Please try again or contact support.";
          }
          
          throw new Error(errorMessage);
        }

        const result = await response.json();
        
        if (!result || !result.id) {
          throw new Error("Invalid response from server. Attendance may not have been saved.");
        }
        
        lastScannedSessionIdRef.current = sessionId;
        setSuccess("Attendance marked successfully! Check your email for confirmation.");

        await fetchAttendanceRecords();
        await fetchStats();

        // Stop scanner after successful scan
        await stopScanner();

        // Clear success message
        setTimeout(() => setSuccess(""), 5000);

        // Reset session ID after delay
        setTimeout(() => {
          lastScannedSessionIdRef.current = null;
        }, 10000);

      } catch (err) {
        console.error("QR Scan Error:", err);
        setError(err.message || "Error scanning QR code. Please try again.");
        setTimeout(() => setError(""), 5000);
        lastScannedSessionIdRef.current = null;
      } finally {
        isProcessingRef.current = false;
        setLoading(false);
        scanTimeoutRef.current = null;
      }
    }, 300);
  }, [student_usn, loading, fetchAttendanceRecords, fetchStats, stopScanner]);

  // Update ref whenever handleQRCodeScan changes
  useEffect(() => {
    handleQRCodeScanRef.current = handleQRCodeScan;
  }, [handleQRCodeScan]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-IN', {
      timeZone: 'Asia/Kolkata',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
  };

  return (
    <div className="attendance-container">
      <div className="attendance-header">
        <h2>Mark Attendance</h2>
      </div>

      {dashboardStats === null && (
        <p className="attendance-stats-loading">Loading stats…</p>
      )}
      {dashboardStats && (
        <div className="attendance-dashboard">
          <div className="stat-card">
            <span className="stat-label">Total Attendance</span>
            <span className="stat-value">{dashboardStats.total_records ?? 0}</span>
          </div>
          <div className="stat-card stat-card--present">
            <span className="stat-label">Present</span>
            <span className="stat-value">{dashboardStats.present_count ?? 0}</span>
          </div>
          <div className="stat-card stat-card--absent">
            <span className="stat-label">Absent</span>
            <span className="stat-value">{dashboardStats.absent_count ?? 0}</span>
          </div>
          <div className="stat-card stat-card--late">
            <span className="stat-label">Late</span>
            <span className="stat-value">{dashboardStats.late_count ?? 0}</span>
          </div>
          <div className="stat-card stat-card--week">
            <span className="stat-label">This Week (Present)</span>
            <span className="stat-value">{dashboardStats.this_week_present ?? 0}</span>
          </div>
        </div>
      )}

      {error && (
        <div className="error-message" onClick={() => setError("")}>
          {error} (Click to dismiss)
        </div>
      )}

      {success && (
        <div className="success-message" onClick={() => setSuccess("")}>
          {success} (Click to dismiss)
        </div>
      )}

      <div className="scanner-section">
        {!scanning ? (
          <div className="scanner-placeholder">
            <div className="scanner-icon-wrapper">
              <FaQrcode className="scanner-icon" />
            </div>
            <h3>QR Code Scanner</h3>
            <p>Click the button below to start scanning QR code for attendance</p>
            <button className="btn-scan" onClick={startScanner}>
              <FaCamera /> Start Scanner
            </button>
          </div>
        ) : (
          <div className="scanner-active">
            <div className="scanner-header">
              <h3>Scan QR Code</h3>
              <p className="scanner-hint">Position the QR code within the frame</p>
            </div>
            <div className="scanner-wrapper">
              <video
                ref={videoRef}
                style={{ width: "100%", maxWidth: "500px", height: "auto" }}
                playsInline
                muted
                autoPlay
                className="qr-reader-container"
              />
              <canvas ref={canvasRef} style={{ display: "none" }} />
              <div className="scanner-overlay">
                <div className="scanner-frame"></div>
                <div className="scanner-corner top-left"></div>
                <div className="scanner-corner top-right"></div>
                <div className="scanner-corner bottom-left"></div>
                <div className="scanner-corner bottom-right"></div>
              </div>
            </div>
            <div className="scanner-controls">
              <button
                className="btn-switch-camera"
                onClick={switchCamera}
                disabled={loading}
                title={`Switch to ${facingMode === "environment" ? "front" : "back"} camera`}
              >
                <FaSyncAlt /> Switch Camera
              </button>
              <button
                className="btn-stop"
                onClick={stopScanner}
                disabled={loading}
              >
                <FaStop /> {loading ? "Processing..." : "Stop Scanner"}
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="attendance-records-section">
        <h3>My Attendance Records</h3>
        {attendanceRecords.length === 0 ? (
          <p>No attendance records found.</p>
        ) : (
          <table className="records-table">
            <thead>
              <tr>
                <th>Session Name</th>
                <th>Marked At</th>
                <th>Status</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {attendanceRecords.map((record) => (
                <tr key={record.id}>
                  <td>{record.session_name || "Unnamed Session"}</td>
                  <td>{formatDate(record.marked_at)}</td>
                  <td>
                    <span className={`status-badge ${record.status}`}>
                      {record.status}
                    </span>
                  </td>
                  <td>{record.notes || "N/A"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default Attendance;
