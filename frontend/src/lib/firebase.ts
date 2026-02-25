import { initializeApp } from "firebase/app";
import { getAnalytics, isSupported } from "firebase/analytics";

const firebaseConfig = {
  apiKey: "AIzaSyB0bieZM56zFvsaH1xsRgzmgUElCjBvkuE",
  authDomain: "aerovillage-3b8df.firebaseapp.com",
  projectId: "aerovillage-3b8df",
  storageBucket: "aerovillage-3b8df.firebasestorage.app",
  messagingSenderId: "471602662262",
  appId: "1:471602662262:web:bf3403593c6bf046ab0857",
  measurementId: "G-7TGJ7GT20C",
};

export const firebaseApp = initializeApp(firebaseConfig);

if (typeof window !== "undefined") {
  isSupported().then((supported) => {
    if (supported) {
      getAnalytics(firebaseApp);
    }
  });
}
