import React from 'react';
import '../styles/ChangeLog.css';
import Card from '../components/Card';

const ChangeLog = () => (
  <div className="container-changeLog container my-5 p-5">
    <div className="col-12">
      {/* <div className="card mb-4 border-0 rounded-4 shadow-sm"> */}
      <Card title='Change Log' headerTag='h2'>
        <p>
          <strong>5-22-2025: A long list of GUI changes</strong><br />
        </p>
        <ul className="list-unstyled">
          <li>Added Crypta 2.0 to Header.</li>
          <li>Changed home page to database and what was the home page to change log.</li>
          <li>Updated URL paths.</li>
          <li>Made the relationship button on details page a teams message link.</li>
          <li>Update database table with pagination.</li>
          <li>Update database with row moving capabilities.</li>
          <li>Rounded table results for future main usage with new database look upcoming.</li>
          <li>Matched Gradient to Workday for details page.</li>
          <li>Updated rounding to better match workday.</li>
          <li>Update primary info with boxes that Bill Weldon preferred.</li>
          <li>Added Main overflow feature for horizontal and vertical main section of details page.</li>
          <li>Added sticky feature to header.</li>
          <li>Added sticky feature to left nav of details page.</li>
          <li>Updated return button to match action button.</li>
          <li>Fixed aspect ratio on photos.</li>
          <li>Shrunk left nav using css.</li>
          <li>Added label for which database you query.</li>
          <li>Added new and improved stat filtering.</li>
          <li>Added new icons for default usage on details pages.</li>
        </ul>
        <p>
          <strong>5-12-2025: Created a search feature for the application</strong><br />
          We can now use the search bar to find detail pages from the crypta database and pull specific detail pages up.
        </p>
        <p>
          <strong>5-12-2025: Added dynamic address query system with Google Maps for physical locations on Details Page.</strong><br />
          Created a basic parser to construct Google Maps queries based on church and school addresses.
        </p>
        <p>
          <strong>5-12-2025: Added locations functionality for basic location data on Details Page.</strong><br />
          Went through and added logic for when location IDs are passed to the details page.
        </p>
        <p>
          <strong>5-12-2025: Added Export to CSV and Excel</strong><br />
          The action buttons for exporting to Excel and CSV are now live! It exports a filtered results file with chosen columns.<br />
        </p>
        <p>
          <strong>5-12-2025: Added count to email recipients in email confirmation</strong><br />
          We now display the total number of recipients before sending, making it easier to verify.<br />
        </p>
        <p>
          <strong>5-12-2025: Created a dynamic Details Page</strong><br />
          The Details page now dynamically renders sections based on the selected record.<br />
        </p>
        <p>
          <strong>5-12-2025: Added Search Filters</strong><br />
          The filter sidebar now supports searching fields and statistic filters.<br />
        </p>
        <p>
          <strong>5-10-2025: Added Column Chooser</strong><br />
          Users can select which columns to display in the results grid.<br />
        </p>
        <p>
          <strong>5-8-2025: Header & GUI Updates</strong><br />
          Updated header styling and custom menu behavior to match the provided design.<br />
        </p>
        <p>
          <strong>5-5-2025: Introduced Action Buttons</strong><br />
          Placeholders for exporting and emailing are in place; attachments and body expansion are functional.<br />
        </p>
        <p>
          <strong>4-25-2025: Entire Filtering & Sorting System Operational</strong><br />
          The enhanced filtering system is fully operational, offering an Amazon-like experience.<br />
        </p>
      </Card>
      {/* </div> */}
    </div>
  </div>
);

export default ChangeLog;
