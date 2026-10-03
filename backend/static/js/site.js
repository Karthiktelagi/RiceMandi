// RiceMandi — progressive enhancement only.
// Every page must work with JavaScript disabled; HTMX then makes it feel fast.
(function () {
  "use strict";

  // The rate board (Milestone 4) and chat thread (Milestone 8) poll themselves.
  // Poll only while the tab is visible: a merchant on a weak connection should
  // not have their battery drained by a background yard that is not changing.
  const POLL_INTERVALS = { "rm-poll-60": 60000, "rm-poll-5": 5000 };

  let timer = null;
  let pending = null;

  function poll(intervalMs) {
    if (timer) {
      window.clearInterval(timer);
      timer = null;
    }
    if (!intervalMs || document.hidden) return;

    // Re-run every intervalMs; skip a tick if the last one is still in flight.
    timer = window.setInterval(() => {
      if (pending) return;
      pending = true;
      Promise.resolve(window.htmx.trigger(document.body, "rmPoll"))
        .finally(() => {
          pending = false;
        });
    }, intervalMs);

    document.addEventListener("visibilitychange", function onVisible() {
      if (!document.hidden) {
        poll(intervalMs);
      } else {
        poll(null);
        document.removeEventListener("visibilitychange", onVisible);
      }
    });
  }

  function currentInterval() {
    const el = document.querySelector("[data-poll-interval]");
    if (!el) return null;
    return POLL_INTERVALS[el.dataset.pollInterval] || null;
  }

  function restartPolling() {
    poll(currentInterval());
  }

  document.addEventListener("DOMContentLoaded", restartPolling);
  // HTMX swaps the body on every poll; re-arm after each swap.
  document.body.addEventListener("htmx:afterSwap", restartPolling);
})();
