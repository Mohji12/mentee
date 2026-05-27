import React from "react";
import '../assets/css/LinkPage.css'

const LinkPage = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-6">
      {/* Profile Section */}
      <div className="text-center">
        <img
          src="https://via.placeholder.com/100"
          alt="Profile"
          className="rounded-full w-24 h-24 border-4 border-white shadow-lg"
        />
        <h2 className="mt-4 text-xl font-bold">Your Name</h2>
        <p className="text-gray-600">Your Bio or Tagline</p>
      </div>

      {/* Links Section */}
      <div className="mt-6 w-full max-w-xs">
        {[
          { name: "Visit Store", url: "https://yourstore.com" },
          { name: "Instagram", url: "https://instagram.com/yourprofile" },
          { name: "YouTube", url: "https://youtube.com/yourchannel" },
        ].map((link, index) => (
          <a
            key={index}
            href={link.url}
            target="_blank"
            rel="noopener noreferrer"
            className="block bg-white text-center text-lg font-medium text-blue-600 p-3 rounded-lg shadow-md mb-3 hover:bg-blue-50 transition"
          >
            {link.name}
          </a>
        ))}
      </div>
    </div>
  );
};

export default LinkPage;
