// Custom JavaScript for enhanced effects

document.addEventListener('DOMContentLoaded', function() {
  // Add glitch effect to logo on click
  const logo = document.querySelector('.md-logo');
  if (logo) {
    logo.addEventListener('click', function() {
      this.style.animation = 'glitch 0.5s ease-in-out';
      setTimeout(() => {
        this.style.animation = '';
      }, 500);
    });
  }

  // Add cyberpunk cursor trail effect (optional, subtle)
  document.addEventListener('mousemove', function(e) {
    const trail = document.createElement('div');
    trail.className = 'cursor-trail';
    trail.style.left = e.pageX + 'px';
    trail.style.top = e.pageY + 'px';
    document.body.appendChild(trail);

    setTimeout(() => {
      trail.remove();
    }, 1000);
  });
});

// Add CSS for cursor trail
const style = document.createElement('style');
style.textContent = `
  .cursor-trail {
    position: absolute;
    width: 4px;
    height: 4px;
    background: var(--cyber-cyan);
    border-radius: 50%;
    pointer-events: none;
    z-index: 9999;
    animation: fade-out 1s ease-out forwards;
    box-shadow: 0 0 10px var(--cyber-cyan);
  }

  @keyframes fade-out {
    to {
      opacity: 0;
      transform: scale(0);
    }
  }
`;
document.head.appendChild(style);
