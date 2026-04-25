/**
 * Cubic spline interpolation for smoothing price charts
 * Uses natural cubic spline algorithm
 */

/**
 * Create a natural cubic spline interpolator
 * @param {number[]} x - x-coordinates (time indices)
 * @param {number[]} y - y-coordinates (price values)
 * @returns {function(number): number} - interpolator function
 */
export function createCubicSpline(x, y) {
  const n = x.length - 1
  if (n < 1) return () => y[0] || 0
  if (n === 1) {
    // Linear interpolation for 2 points
    return (t) => y[0] + ((y[1] - y[0]) * (t - x[0])) / (x[1] - x[0])
  }

  // Calculate h values (intervals)
  const h = []
  for (let i = 0; i < n; i++) {
    h[i] = x[i + 1] - x[i]
  }

  // Calculate alpha values
  const alpha = [0]
  for (let i = 1; i < n; i++) {
    alpha[i] =
      (3 / h[i]) * (y[i + 1] - y[i]) - (3 / h[i - 1]) * (y[i] - y[i - 1])
  }

  // Solve tridiagonal system for second derivatives (c)
  const l = [1]
  const mu = [0]
  const z = [0]

  for (let i = 1; i < n; i++) {
    l[i] = 2 * (x[i + 1] - x[i - 1]) - h[i - 1] * mu[i - 1]
    mu[i] = h[i] / l[i]
    z[i] = (alpha[i] - h[i - 1] * z[i - 1]) / l[i]
  }

  l[n] = 1
  z[n] = 0
  const c = new Array(n + 1).fill(0)
  const b = new Array(n).fill(0)
  const d = new Array(n).fill(0)

  for (let j = n - 1; j >= 0; j--) {
    c[j] = z[j] - mu[j] * c[j + 1]
    b[j] = (y[j + 1] - y[j]) / h[j] - (h[j] * (c[j + 1] + 2 * c[j])) / 3
    d[j] = (c[j + 1] - c[j]) / (3 * h[j])
  }

  // Return interpolator function
  return function (t) {
    // Find the interval containing t
    let i = 0
    for (let j = 0; j < n; j++) {
      if (t >= x[j] && t <= x[j + 1]) {
        i = j
        break
      }
    }
    if (t < x[0]) i = 0
    if (t > x[n]) i = n - 1

    const dx = t - x[i]
    return y[i] + b[i] * dx + c[i] * dx * dx + d[i] * dx * dx * dx
  }
}

/**
 * Smooth price data using cubic spline interpolation
 * @param {Array<{timestamp: string, close: number}>} data - price points
 * @param {number} pointsPerSegment - number of interpolated points between each original point
 * @returns {Array<{timestamp: string, close: number, original: boolean}>} - smoothed data
 */
export function smoothPriceData(data, pointsPerSegment = 4) {
  if (!data || data.length < 2) return data

  const n = data.length
  const x = Array.from({ length: n }, (_, i) => i)
  const y = data.map((d) => d.close)

  const spline = createCubicSpline(x, y)

  const result = []
  const totalPoints = (n - 1) * pointsPerSegment + 1

  for (let i = 0; i < totalPoints; i++) {
    const t = i / pointsPerSegment
    const dataIndex = Math.min(Math.floor(t), n - 1)
    const interpolatedValue = spline(t)

    result.push({
      timestamp: data[dataIndex].timestamp,
      close: interpolatedValue,
      high: data[dataIndex].high,
      low: data[dataIndex].low,
      open: data[dataIndex].open,
      volume: data[dataIndex].volume,
      original: Number.isInteger(t) && t >= 0 && t < n,
    })
  }

  return result
}

/**
 * Simple moving average smoothing (fallback)
 * @param {number[]} data - array of values
 * @param {number} window - window size
 * @returns {number[]} - smoothed values
 */
export function movingAverageSmooth(data, window = 3) {
  if (!data || data.length === 0) return data

  const result = []
  for (let i = 0; i < data.length; i++) {
    const start = Math.max(0, i - Math.floor(window / 2))
    const end = Math.min(data.length, i + Math.ceil(window / 2))
    const sum = data.slice(start, end).reduce((a, b) => a + b, 0)
    result.push(sum / (end - start))
  }
  return result
}
