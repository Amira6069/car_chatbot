import React from 'react';
import { Outlet } from 'react-router-dom';

const EvaluatorLayout = () => {
  return (
    <div className="layout-container">
      <Outlet />
    </div>
  );
};

export default EvaluatorLayout;