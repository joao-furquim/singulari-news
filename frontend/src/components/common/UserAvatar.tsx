import { Box } from '@mui/material';
import { getInitials, getAvatarColor } from '../../utils/avatar';

interface UserAvatarProps {
  name: string;
  size?: number;
}

export function UserAvatar({ name, size = 30 }: UserAvatarProps) {
  const { bg, color } = getAvatarColor(name);
  const initials = getInitials(name) || '?';

  return (
    <Box
      sx={{
        width: size,
        height: size,
        borderRadius: '50%',
        background: `linear-gradient(135deg, ${bg}, ${color}33)`,
        border: `1.5px solid ${color}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: size * 0.38,
        fontWeight: 600,
        color,
        flexShrink: 0,
        userSelect: 'none',
        letterSpacing: '0.02em',
      }}
    >
      {initials}
    </Box>
  );
}
