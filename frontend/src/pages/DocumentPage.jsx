import React from 'react';
import Sidebar from '../components/Sidebar';
import ProgressSteps from '../components/ProgressSteps';
import DocumentViewer from '../components/DocumentPreview/DocumentViewer';

export const DocumentPage = () => {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-100/70 font-sans">
      <div className="no-print">
        <Sidebar />
      </div>

      <div className="flex-1 flex flex-col h-full overflow-hidden min-w-0">
        <div className="no-print">
          <ProgressSteps activeStep={5} />
        </div>

        <div className="flex-1 overflow-y-auto p-4 sm:p-8">
          <DocumentViewer isEmbedded={false} />
        </div>
      </div>
    </div>
  );
};

export default DocumentPage;
