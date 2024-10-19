/*!
       * Color mode toggler for Bootstrap's docs (https://getbootstrap.com/)
       * Copyright 2011-2024 The Bootstrap Authors
       * Licensed under the Creative Commons Attribution 3.0 Unported License.
       * Modified by Simpleqode
       */
    
(() => {
  'use strict';

  const getStoredTheme = () => localStorage.getItem('theme');
  const setStoredTheme = (theme) => localStorage.setItem('theme', theme);

  const getPreferredTheme = () => {
    const storedTheme = getStoredTheme();
    if (storedTheme) {
      return storedTheme;
    }

    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  };

  const setTheme = (theme) => {
    if (theme === 'auto') {
      document.documentElement.setAttribute('data-bs-theme', window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    } else {
      document.documentElement.setAttribute('data-bs-theme', theme);
    }
  };

  setTheme(getPreferredTheme());

  const showActiveTheme = (theme, focus = false) => {
    const themeSwitchers = document.querySelectorAll('[data-bs-theme-switcher]');

    themeSwitchers.forEach((themeSwitcher) => {
      const themeSwitcherIcon = themeSwitcher.querySelector('.material-symbols-outlined');
      themeSwitcherIcon.innerHTML = theme === 'light' ? 'light_mode' : theme === 'dark' ? 'dark_mode' : 'contrast';

      if (focus) {
        themeSwitcher.focus();
      }
    });

    document.querySelectorAll('[data-bs-theme-value]').forEach((element) => {
      element.classList.remove('active');
      element.setAttribute('aria-pressed', 'false');

      if (element.getAttribute('data-bs-theme-value') === theme) {
        element.classList.add('active');
        element.setAttribute('aria-pressed', 'true');
      }
    });
  };

  const refreshCharts = () => {
    const charts = document.querySelectorAll('.chart-canvas');

    charts.forEach((chart) => {
      const chartId = chart.getAttribute('id');
      const instance = Chart.getChart(chartId);

      if (!instance) {
        return;
      }

      if (instance.options.scales.y) {
        instance.options.scales.y.grid.color = getComputedStyle(document.documentElement).getPropertyValue('--bs-border-color');
        instance.options.scales.y.ticks.color = getComputedStyle(document.documentElement).getPropertyValue('--bs-secondary-color');
      }

      if (instance.options.scales.x) {
        instance.options.scales.x.ticks.color = getComputedStyle(document.documentElement).getPropertyValue('--bs-secondary-color');
      }

      if (instance.options.elements.arc) {
        instance.options.elements.arc.borderColor = getComputedStyle(document.documentElement).getPropertyValue('--bs-body-bg');
        instance.options.elements.arc.hoverBorderColor = getComputedStyle(document.documentElement).getPropertyValue('--bs-body-bg');
      }

      instance.update();
    });
  };

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    const storedTheme = getStoredTheme();
    if (storedTheme !== 'light' && storedTheme !== 'dark') {
      setTheme(getPreferredTheme());
    }
  });

  window.addEventListener('DOMContentLoaded', () => {
    showActiveTheme(getPreferredTheme());

    document.querySelectorAll('[data-bs-theme-value]').forEach((toggle) => {
      toggle.addEventListener('click', (e) => {
        e.preventDefault();
        const theme = toggle.getAttribute('data-bs-theme-value');
        setStoredTheme(theme);
        setTheme(theme);
        showActiveTheme(theme, true);
        refreshCharts();
      });
    });
  });
})();