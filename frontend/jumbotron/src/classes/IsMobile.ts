export default function isMobileDevice(): boolean {
    const userAgent: string = navigator.userAgent;

    // Check for iPhone, iPad, iPod
    if (/iPhone|iPod|iPad/.test(userAgent)) {
        return true;
    }

    // Check for Android
    if (/android/i.test(userAgent)) {
        return true;
    }

    if (window.innerWidth < 800) {
        return true;
    }

    // If neither iPhone/iPod/iPad nor Android was detected, return false
    return false;
}