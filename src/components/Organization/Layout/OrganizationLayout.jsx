import React from 'react';

const OrganizationLayout = () => {
    return (
        <div>
            <Header />
            <Sidebar />
            <Outlet />
            <Footer />
        </div>
    );
};

export default OrganizationLayout;