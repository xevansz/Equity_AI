/**
 * src/websocket/streamClient.js  ← NEW module
 *
 * Manages the single persistent WebSocket connection to /ws/stream.
 * Supports subscribe / unsubscribe / auto-reconnect / heartbeat detection.
 *
 * Usage:
 *   import { streamClient } from '@/websocket/streamClient'
 *   streamClient.connect()
 *   const unsub = streamClient.on('quote', handler)
 *   streamClient.subscribe(['AAPL'], 'US')
 *   unsub()
 */

const WS_URL = (import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000') + '/ws/stream';
const RECONNECT_DELAY_MS  = 3_000;
const MAX_RECONNECT_DELAY = 30_000;
const HEARTBEAT_TIMEOUT   = 45_000; // disconnect if no message in 45s

class StreamClient {
  constructor() {
    this._ws              = null;
    this._listeners       = {};          // eventType → Set<handler>
    this._reconnectDelay  = RECONNECT_DELAY_MS;
    this._intentionalClose = false;
    this._heartbeatTimer  = null;
    this._pendingSubs     = [];          // queued while connecting
    this._status          = 'disconnected'; // 'connecting' | 'connected' | 'disconnected'
  }

  // ── Public API ─────────────────────────────────────────────────────────────

  connect() {
    if (this._ws && this._ws.readyState < 2) return; // already open/connecting
    this._intentionalClose = false;
    this._status = 'connecting';
    this._emit('status', { status: 'connecting' });

    this._ws = new WebSocket(WS_URL);
    this._ws.onopen    = this._onOpen.bind(this);
    this._ws.onmessage = this._onMessage.bind(this);
    this._ws.onclose   = this._onClose.bind(this);
    this._ws.onerror   = this._onError.bind(this);
  }

  disconnect() {
    this._intentionalClose = true;
    this._clearHeartbeat();
    this._ws?.close();
    this._status = 'disconnected';
  }

  /**
   * Subscribe to symbols for real-time quotes.
   * @param {string[]} symbols
   * @param {string}   market   "US" | "INDIA"
   * @param {string}   interval "1min" | "5min" ...
   * @param {string}   exchange "NSE_EQ" | "NSE" | ...
   */
  subscribe(symbols, market = 'US', interval = '1min', exchange = 'NSE_EQ') {
    const msg = { action: 'subscribe', symbols, market, interval, exchange };
    this._send(msg);
  }

  unsubscribe(symbols) {
    this._send({ action: 'unsubscribe', symbols });
  }

  ping() {
    this._send({ action: 'ping' });
  }

  /**
   * Register a handler for a message type.
   * @param {'quote'|'candle'|'error'|'status'|'heartbeat'|'pong'|'info'} type
   * @param {Function} handler
   * @returns {Function} unsubscribe function
   */
  on(type, handler) {
    if (!this._listeners[type]) this._listeners[type] = new Set();
    this._listeners[type].add(handler);
    return () => this._listeners[type]?.delete(handler);
  }

  get status() { return this._status; }

  // ── Private ────────────────────────────────────────────────────────────────

  _send(payload) {
    if (this._ws?.readyState === WebSocket.OPEN) {
      this._ws.send(JSON.stringify(payload));
    } else {
      // Queue subscription messages while connecting
      if (payload.action === 'subscribe') {
        this._pendingSubs.push(payload);
      }
    }
  }

  _onOpen() {
    this._status = 'connected';
    this._reconnectDelay = RECONNECT_DELAY_MS;
    this._resetHeartbeat();
    this._emit('status', { status: 'connected' });

    // Flush pending subscriptions
    this._pendingSubs.forEach(msg => this._send(msg));
    this._pendingSubs = [];
  }

  _onMessage(event) {
    this._resetHeartbeat();
    try {
      const msg = JSON.parse(event.data);
      this._emit(msg.type ?? 'unknown', msg);
    } catch {
      console.warn('[StreamClient] Non-JSON message:', event.data);
    }
  }

  _onClose(event) {
    this._clearHeartbeat();
    this._status = 'disconnected';
    this._emit('status', { status: 'disconnected', code: event.code });

    if (!this._intentionalClose) {
      setTimeout(() => {
        this._reconnectDelay = Math.min(this._reconnectDelay * 1.5, MAX_RECONNECT_DELAY);
        this.connect();
      }, this._reconnectDelay);
    }
  }

  _onError(err) {
    console.error('[StreamClient] WebSocket error:', err);
    this._emit('error', { message: 'WebSocket connection error' });
  }

  _emit(type, data) {
    this._listeners[type]?.forEach(h => {
      try { h(data); } catch (e) { console.error(`[StreamClient] handler error (${type}):`, e); }
    });
  }

  _resetHeartbeat() {
    this._clearHeartbeat();
    this._heartbeatTimer = setTimeout(() => {
      console.warn('[StreamClient] Heartbeat timeout — reconnecting');
      this._ws?.close();
    }, HEARTBEAT_TIMEOUT);
  }

  _clearHeartbeat() {
    if (this._heartbeatTimer) {
      clearTimeout(this._heartbeatTimer);
      this._heartbeatTimer = null;
    }
  }
}

// App-wide singleton
export const streamClient = new StreamClient();
