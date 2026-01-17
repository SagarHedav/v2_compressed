const guestChatCount = new Map();

export const chatLimit = (req, res, next) => {
  // If user is logged in, allow unlimited access
  if (req.user) {
    return next();
  }

  // Identify guest by IP
  const ip = req.ip;
  const count = guestChatCount.get(ip) || 0;

  if (count >= 15) {
    return res.status(403).json({
      message: "Chat limit reached. Please login to continue."
    });
  }

  guestChatCount.set(ip, count + 1);
  next();
};
