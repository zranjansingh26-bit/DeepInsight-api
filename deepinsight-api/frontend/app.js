/**
 * DeepInsights — Full Landing Page Scripts
 */

document.addEventListener('DOMContentLoaded', () => {

  // ═══════════════════════════════════════════════════
  // 1. SCROLL REVEAL ANIMATIONS
  // ═══════════════════════════════════════════════════
  const revealElements = document.querySelectorAll('.reveal-up, .reveal-left, .reveal-right');
  
  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('active');
        // If it's the chat section, trigger chat sequence
        if (entry.target.classList.contains('chat-ui-wrapper') && !window.chatTriggered) {
          window.chatTriggered = true;
          runChatSequence();
        }
        // If it's ecosystem pipeline, trigger node activation
        if (entry.target.classList.contains('pipeline-step') && !window.ecoTriggered) {
          window.ecoTriggered = true;
          animateEcosystem();
        }
        observer.unobserve(entry.target);
      }
    });
  }, { rootMargin: '0px 0px -100px 0px', threshold: 0.1 });

  revealElements.forEach(el => revealObserver.observe(el));


  // ═══════════════════════════════════════════════════
  // 2. HERO CHARTS (Chart.js)
  // ═══════════════════════════════════════════════════
  Chart.defaults.color = '#94a3b8';
  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.elements.point.radius = 0;
  Chart.defaults.plugins.legend.display = false;
  Chart.defaults.plugins.tooltip.enabled = false;

  const noGrid = { x: { display: false }, y: { display: false } };

  // Helper for gradients
  function getGradient(ctx, colorStart, colorEnd) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 150);
    gradient.addColorStop(0, colorStart);
    gradient.addColorStop(1, colorEnd);
    return gradient;
  }

  // Chart 1: Small top left (Green Line)
  const ctx1 = document.getElementById('hero-chart-1').getContext('2d');
  new Chart(ctx1, {
    type: 'line',
    data: {
      labels: ['1','2','3','4','5','6','7'],
      datasets: [{
        data: [10, 25, 20, 45, 30, 50, 65],
        borderColor: '#10b981',
        borderWidth: 2,
        tension: 0.4
      }]
    },
    options: { responsive: true, maintainAspectRatio: false, scales: noGrid }
  });

  // Chart 2: Center Mini 1 (Orange Area)
  const ctx2 = document.getElementById('hero-chart-2').getContext('2d');
  new Chart(ctx2, {
    type: 'line',
    data: {
      labels: ['1','2','3','4','5','6'],
      datasets: [{
        data: [5, 15, 10, 35, 25, 45],
        borderColor: '#f59e0b',
        backgroundColor: getGradient(ctx2, 'rgba(245, 158, 11, 0.4)', 'transparent'),
        fill: true,
        tension: 0.4
      }]
    },
    options: { responsive: true, maintainAspectRatio: false, scales: noGrid }
  });

  // Chart 3: Center Mini 2 (Green Area)
  const ctx3 = document.getElementById('hero-chart-3').getContext('2d');
  new Chart(ctx3, {
    type: 'line',
    data: {
      labels: ['1','2','3','4','5','6'],
      datasets: [{
        data: [20, 15, 30, 25, 50, 40],
        borderColor: '#10b981',
        backgroundColor: getGradient(ctx3, 'rgba(16, 185, 129, 0.4)', 'transparent'),
        fill: true,
        tension: 0.4
      }]
    },
    options: { responsive: true, maintainAspectRatio: false, scales: noGrid }
  });

  // Chart 4: Center Bottom (Blue Bar)
  const ctx4 = document.getElementById('hero-chart-4').getContext('2d');
  new Chart(ctx4, {
    type: 'bar',
    data: {
      labels: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct'],
      datasets: [{
        data: [30, 45, 25, 60, 40, 75, 55, 80, 65, 90],
        backgroundColor: '#3b82f6',
        borderRadius: 4
      }]
    },
    options: { responsive: true, maintainAspectRatio: false, scales: noGrid }
  });

  // Chart 5: Small bottom right (Blue Line with points)
  const ctx5 = document.getElementById('hero-chart-5').getContext('2d');
  new Chart(ctx5, {
    type: 'line',
    data: {
      labels: ['1','2','3','4','5'],
      datasets: [{
        data: [100, 120, 115, 140, 160],
        borderColor: '#00e5ff',
        backgroundColor: getGradient(ctx5, 'rgba(0, 229, 255, 0.3)', 'transparent'),
        borderWidth: 2,
        fill: true,
        tension: 0.3,
        pointRadius: 3,
        pointBackgroundColor: '#fff'
      }]
    },
    options: { responsive: true, maintainAspectRatio: false, scales: noGrid }
  });


  // ═══════════════════════════════════════════════════
  // 3. TITLE REVEAL (DEEPINSIGHTS)
  // ═══════════════════════════════════════════════════
  function revealTitle() {
    const text = "DEEPINSIGHTS";
    const aboveEl = document.getElementById('title-above');
    const belowEl = document.getElementById('title-below');
    
    aboveEl.innerHTML = '';
    belowEl.innerHTML = '';

    for (let i = 0; i < text.length; i++) {
      const spanAbove = document.createElement('span');
      spanAbove.style.opacity = '0';
      spanAbove.textContent = text[i];
      spanAbove.style.transition = `opacity 0.4s ease, filter 0.4s ease, transform 0.6s cubic-bezier(0.16,1,0.3,1)`;
      spanAbove.style.transitionDelay = `${0.5 + (i * 0.08)}s`;
      spanAbove.style.filter = 'blur(10px)';
      spanAbove.style.transform = 'translateY(20px)';
      
      const spanBelow = spanAbove.cloneNode(true);

      aboveEl.appendChild(spanAbove);
      belowEl.appendChild(spanBelow);

      // Trigger animation
      setTimeout(() => {
        spanAbove.style.opacity = '1';
        spanAbove.style.filter = 'blur(0)';
        spanAbove.style.transform = 'translateY(0)';
        
        spanBelow.style.opacity = '1';
        spanBelow.style.filter = 'blur(0)';
        spanBelow.style.transform = 'translateY(0)';
      }, 100);
    }
  }
  revealTitle();


  // ═══════════════════════════════════════════════════
  // 4. ECOSYSTEM PIPELINE ANIMATION
  // ═══════════════════════════════════════════════════
  function animateEcosystem() {
    const nodes = document.querySelectorAll('.step-node');
    let delay = 0;
    nodes.forEach((node, index) => {
      setTimeout(() => {
        nodes.forEach(n => n.classList.remove('active-node'));
        node.classList.add('active-node');
      }, delay);
      delay += 800;
    });
  }

  // ═══════════════════════════════════════════════════
  // 5. CHAT SIMULATION
  // ═══════════════════════════════════════════════════
  function addChatMessage(sender, text) {
    const chatBody = document.getElementById('chat-body');
    const div = document.createElement('div');
    div.className = `msg ${sender}`;
    div.innerHTML = `<div class="msg-bubble">${text}</div>`;
    
    // Animate in
    div.style.opacity = '0';
    div.style.transform = 'translateY(10px)';
    div.style.transition = 'all 0.3s ease';
    
    chatBody.appendChild(div);
    
    // Trigger reflow
    void div.offsetWidth;
    
    div.style.opacity = '1';
    div.style.transform = 'translateY(0)';
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  function showTyping() {
    const chatBody = document.getElementById('chat-body');
    const div = document.createElement('div');
    div.className = 'msg bot typing-indicator';
    div.innerHTML = `<div class="msg-bubble" style="color:var(--cyan); letter-spacing:2px; font-weight:bold;">...</div>`;
    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
    return div;
  }

  function runChatSequence() {
    setTimeout(() => {
      addChatMessage('user', 'What were the total anomalies detected in Q3 across EU servers?');
      
      setTimeout(() => {
        const typing = showTyping();
        
        setTimeout(() => {
          typing.remove();
          addChatMessage('bot', 'In Q3, the anomaly detection engine flagged 1,245 events in the EU region. 98% of these were automatically mitigated. I can generate a detailed time-series visualization if you like.');
          
          setTimeout(() => {
            addChatMessage('user', 'Yes, plot the weekly trend.');
            
            setTimeout(() => {
              const typing2 = showTyping();
              setTimeout(() => {
                typing2.remove();
                addChatMessage('bot', 'Generating visualization based on your request... [Chart Rendering Placeholder]');
              }, 1200);
            }, 600);
            
          }, 3500);
          
        }, 1500);
      }, 500);
    }, 800);
  }

});
