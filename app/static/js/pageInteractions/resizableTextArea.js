// TO USE PASTE THIS JINJA STRUCTURE (create the proper form in forms.py first), styles can be found in css/pageInteractions/filters.css and using bootstrap, script in js/pageInteractions/resizableTextArea.js.
// {{ form.**TextAreaName**.label }}
// {{ form.**TextAreaName**(class='form-control resizable') }}

// resizable text area interaction
class ResizableTextArea {
    constructor(textarea) {
        this.textarea = textarea;
        this.resizeHandle = document.createElement('div');
        this.resizeHandle.classList.add('resizeHandle');
        this.textarea.parentNode.appendChild(this.resizeHandle);
        
        // add local event listeners
        this.addEventListeners();
    };
  
    addEventListeners() {
        this.resizeHandle.addEventListener('mousedown', (e) => this.onMouseDown(e));
    };
  
    onMouseDown(e) {
        e.preventDefault(); 
  
        // get dimensions for resizing
        const initialHeight = this.textarea.offsetHeight;
        const initialMouseY = e.clientY;

        // should've done this structure for filter.js but oh well lol
        const onMouseMove = (event) => {
            const diff = event.clientY - initialMouseY;
            this.textarea.style.height = `${initialHeight + diff}px`;
        };
  
        // remove global listeners to avoid propagation
        const onMouseUp = () => {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        };
        
        // initialise global event listeners
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    };
};
// initialist ResizableTextAreas
const textareas = document.querySelectorAll('textarea.resizable');
textareas.forEach(textarea => new ResizableTextArea(textarea));