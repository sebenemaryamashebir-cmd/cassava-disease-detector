import { useRef, useState } from "react";
import { Sprout, UploadCloud } from "lucide-react";

const MAX_BYTES = 5 * 1024 * 1024;
const ACCEPTED_TYPES = ["image/png", "image/jpeg", "image/jpg"];

export default function UploadZone({ onFileSelected, onValidationError }) {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);

  const validateAndSelect = (fileList) => {
    const file = fileList && fileList[0];
    if (!file) return;

    if (!ACCEPTED_TYPES.includes(file.type)) {
      onValidationError?.("Please upload a PNG, JPG or JPEG image.");
      return;
    }
    if (file.size > MAX_BYTES) {
      onValidationError?.("That image is larger than 5 MB. Please choose a smaller file.");
      return;
    }
    onFileSelected(file);
  };

  return (
    <label
      className={"dropzone" + (dragOver ? " drag-over" : "")}
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        validateAndSelect(e.dataTransfer.files);
      }}
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
      }}
    >
      <div className="dropzone-icon">
        <Sprout size={26} strokeWidth={2} />
      </div>
      <div className="dropzone-title">Drop your cassava leaf image here</div>
      <div className="dropzone-or">or browse from your device</div>
      <span
        className="btn btn-primary"
        onClick={(e) => {
          e.preventDefault();
          inputRef.current?.click();
        }}
      >
        <UploadCloud size={16} />
        Choose Image
      </span>
      <div className="dropzone-hint">PNG, JPG or JPEG • Maximum 5 MB</div>
      <div className="dropzone-tip">Tip: for best results, use a clear image showing the entire leaf.</div>
      <input
        ref={inputRef}
        type="file"
        accept="image/png, image/jpeg"
        aria-label="Upload a cassava leaf image"
        onChange={(e) => validateAndSelect(e.target.files)}
      />
    </label>
  );
}
