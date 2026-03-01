import React from 'react';
import { Outlet } from 'react-router-dom';

const AdminLayout = () => {
  return (
    <div className="layout-container">
      <Outlet />
    </div>
  );
};

export default AdminLayout;