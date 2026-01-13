import { createContext, useContext, useState, useEffect } from "react";

const UIContext = createContext();

export function UIProvider({ children }) {
    const [isShootingStarsEnabled, setIsShootingStarsEnabled] = useState(() => {
        const saved = localStorage.getItem("shootingStarsEnabled");
        return saved !== null ? JSON.parse(saved) : true;
    });

    const [isBubblesEnabled, setIsBubblesEnabled] = useState(() => {
        const saved = localStorage.getItem("bubblesEnabled");
        return saved !== null ? JSON.parse(saved) : true;
    });

    const toggleShootingStars = () => {
        setIsShootingStarsEnabled(prev => {
            const newValue = !prev;
            localStorage.setItem("shootingStarsEnabled", JSON.stringify(newValue));
            return newValue;
        });
    };

    const toggleBubbles = () => {
        setIsBubblesEnabled(prev => {
            const newValue = !prev;
            localStorage.setItem("bubblesEnabled", JSON.stringify(newValue));
            return newValue;
        });
    };

    return (
        <UIContext.Provider value={{
            isShootingStarsEnabled,
            toggleShootingStars,
            isBubblesEnabled,
            toggleBubbles
        }}>
            {children}
        </UIContext.Provider>
    );
}

export function useUI() {
    return useContext(UIContext);
}
