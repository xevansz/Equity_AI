import { useContext } from "react"
import { Sun, Moon } from "lucide-react"
import { ThemeContext } from "../context/ThemeContext"

const ThemeToggle = () => {
  const { theme, setTheme } = useContext(ThemeContext)

  return (
    <button
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
      className="p-2 rounded-lg bg-surface hover:bg-surface/80 transition-colors text-text"
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
    >
      {theme === 'light' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
    </button>
  )
}

export default ThemeToggle