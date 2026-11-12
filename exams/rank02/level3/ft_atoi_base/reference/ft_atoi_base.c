static int	digit_value(char c)
{
	if (c >= '0' && c <= '9')
		return (c - '0');
	if (c >= 'a' && c <= 'f')
		return (c - 'a' + 10);
	if (c >= 'A' && c <= 'F')
		return (c - 'A' + 10);
	return (100);
}

int	ft_atoi_base(const char *str, int str_base)
{
	int	sign;
	int	result;

	sign = 1;
	result = 0;
	if (*str == '-')
	{
		sign = -1;
		str++;
	}
	while (digit_value(*str) < str_base)
	{
		result = result * str_base + digit_value(*str);
		str++;
	}
	return (result * sign);
}
