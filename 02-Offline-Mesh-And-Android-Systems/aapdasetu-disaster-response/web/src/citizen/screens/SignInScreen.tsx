import React, { useState } from 'react';
import {
  Phone,
  User,
  Home,
  MapPin,
  Landmark,
  ChevronDown,
  ArrowRight,
  ArrowLeft,
  Info,
  Check,
  Mail,
} from 'lucide-react';
import { UserProfile } from '../types';

import { api } from '../../services/api';

interface SignInScreenProps {
  onSignInSuccess?: (profile: Partial<UserProfile>) => void;
  onSuccessSignIn?: (phone: string) => void;
  onBack?: () => void;
}

export const SignInScreen: React.FC<SignInScreenProps> = ({
  onSignInSuccess,
  onSuccessSignIn,
  onBack,
}) => {
  const [phoneNumber, setPhoneNumber] = useState('9876543210');
  const [email, setEmail] = useState('sahay1382@gmail.com');
  const [fullName, setFullName] = useState('Rahul Sharma');
  const [address, setAddress] = useState('Sarkhej - Gandhinagar Hwy');
  const [city, setCity] = useState('Ahmedabad');
  const [stateVal, setStateVal] = useState('Gujarat');
  const [verified, setVerified] = useState(true);
  const [showOtpModal, setShowOtpModal] = useState(false);
  const [otp, setOtp] = useState(['1', '2', '3', '4', '5', '6']);
  const [sendingOtp, setSendingOtp] = useState(false);
  const [otpNotice, setOtpNotice] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSendingOtp(true);
    setOtpNotice('Sending 6-digit OTP to your Gmail...');
    try {
      const res = await api.sendOtp({ email: email || 'sahay1382@gmail.com', phone: phoneNumber, purpose: 'login' });
      if (res.success && res.data?.devHint) {
        setOtp(res.data.devHint.split(''));
        setOtpNotice('OTP sent! Check your inbox (' + (email || 'sahay1382@gmail.com') + ')');
      }
    } catch (e) {
      console.warn('Fallback to demo OTP:', e);
    } finally {
      setSendingOtp(false);
      setShowOtpModal(true);
    }
  };

  const handleVerifyOtp = async () => {
    const code = otp.join('');
    try {
      const res = await api.verifyOtp({ email: email || 'sahay1382@gmail.com', phone: phoneNumber, otp: code });
      if (res.success && res.data) {
        localStorage.setItem('aapdasetu_token', res.data.token);
        localStorage.setItem('sahay_user', JSON.stringify(res.data.user));
      }
    } catch (e) {
      console.warn('Proceeding with local demo verification:', e);
    }

    const finalName = fullName.trim() || 'Amit Sharma';
    const finalPhone = phoneNumber.trim() ? `+91 ${phoneNumber.trim()}` : '+91 98765 43210';
    const finalAddress = address.trim() || 'Sarkhej - Gandhinagar Hwy';
    const finalCity = city.trim() || 'Ahmedabad';
    const finalState = stateVal.trim() || 'Gujarat';

    const profileData: Partial<UserProfile> = {
      fullName: finalName,
      name: finalName,
      email: email || 'sahay1382@gmail.com',
      phone: finalPhone,
      address: finalAddress,
      city: finalCity,
      state: finalState,
      verified: true,
    };
    if (onSignInSuccess) {
      onSignInSuccess(profileData);
    }
    if (onSuccessSignIn) {
      onSuccessSignIn(finalPhone);
    }
  };

  const handleQuickDemoFill = () => {
    setPhoneNumber('98765 43210');
    setFullName('Rahul Sharma');
    setAddress('Sarkhej - Gandhinagar Hwy');
    setCity('Ahmedabad');
    setStateVal('Gujarat');
    setVerified(true);
  };

  return (
    <main
      className="w-full bg-[#F6F8FA] min-h-full flex flex-col justify-between overflow-y-auto"
      data-purpose="mobile-screen-frame"
    >
      <div className="flex-1 flex flex-col px-4 pt-3 pb-6">
        {/* Top Back Navigation Arrow */}
        <div className="flex items-center justify-between mb-2">
          <button
            aria-label="Go Back"
            type="button"
            onClick={onBack || (() => {})}
            className="p-1 -ml-1 text-slate-900 hover:text-slate-600 transition-colors focus:outline-none cursor-pointer"
          >
            <ArrowLeft className="w-5 h-5 stroke-[2.4]" />
          </button>
          <button
            type="button"
            onClick={handleQuickDemoFill}
            className="text-[11px] font-semibold text-red-600 bg-red-50 hover:bg-red-100 px-2.5 py-1 rounded-full border border-red-200 transition-colors cursor-pointer"
          >
            Fill Sample Data
          </button>
        </div>

        {/* Header Avatar Section */}
        <div className="flex flex-col items-center pt-1 pb-4">
          {/* Centered Avatar with soft red glow */}
          <div className="w-20 h-20 rounded-full bg-red-100/70 flex items-center justify-center mb-3 text-red-600 shadow-inner">
            <svg
              className="w-11 h-11 fill-current"
              viewBox="0 0 24 24"
            >
              <path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z" />
            </svg>
          </div>

          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Welcome Back
          </h1>
          <p className="text-xs font-normal text-slate-500 mt-1">
            Sign in to continue
          </p>
        </div>

        {/* Card Form Container */}
        <form
          className="bg-white rounded-3xl p-5 shadow-xs border border-slate-200/60 space-y-3.5 text-left"
          data-purpose="registration-form"
          onSubmit={handleSubmit}
        >
          {/* Emergency Number */}
          <div className="space-y-1.5" data-purpose="input-emergency-phone">
            <div className="flex items-center justify-between">
              <label
                className="font-bold text-slate-800 text-xs"
                htmlFor="phone-number"
              >
                Emergency Number
              </label>
              <span className="text-[10px] text-slate-400 flex items-center gap-1 font-normal">
                <Info className="w-3 h-3 text-slate-400 shrink-0" />
                We'll contact you in case of emergency
              </span>
            </div>
            <div className="flex items-center border border-slate-200 rounded-xl px-3 py-2.5 bg-white focus-within:ring-2 focus-within:ring-red-500 focus-within:border-transparent transition-all">
              <div className="flex items-center space-x-1 pr-2.5 text-slate-700">
                <Phone className="w-4 h-4 text-red-600 fill-red-600 shrink-0" />
                <span className="text-xs font-semibold text-slate-800 ml-1">+91</span>
                <ChevronDown className="w-3 h-3 text-slate-400 ml-0.5" />
              </div>
              <div className="h-4 w-px bg-slate-200 mx-2" />
              <input
                className="w-full text-xs bg-transparent border-0 p-0 text-slate-800 placeholder-slate-400 focus:ring-0 focus:outline-none"
                id="phone-number"
                placeholder="Enter your mobile number"
                type="tel"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
              />
            </div>
          </div>

          {/* Email for Real Gmail OTP */}
          <div className="space-y-1.5" data-purpose="input-email">
            <div className="flex items-center justify-between">
              <label
                className="font-bold text-slate-800 text-xs"
                htmlFor="email-address"
              >
                Gmail Address (For OTP Verification)
              </label>
              <span className="text-[10px] text-emerald-600 font-semibold flex items-center gap-1">
                Gmail OTP Active
              </span>
            </div>
            <div className="flex items-center border border-slate-200 rounded-xl px-3 py-2.5 bg-white focus-within:ring-2 focus-within:ring-red-500 focus-within:border-transparent transition-all">
              <Mail className="w-4 h-4 text-slate-400 shrink-0 mr-2.5" />
              <input
                className="w-full text-xs bg-transparent border-0 p-0 text-slate-800 placeholder-slate-400 focus:ring-0 focus:outline-none"
                id="email-address"
                placeholder="sahay1382@gmail.com"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>

          {/* Full Name */}
          <div className="space-y-1.5" data-purpose="input-full-name">
            <label
              className="block font-bold text-slate-800 text-xs"
              htmlFor="full-name"
            >
              Full Name
            </label>
            <div className="flex items-center border border-slate-200 rounded-xl px-3 py-2.5 bg-white focus-within:ring-2 focus-within:ring-red-500 focus-within:border-transparent transition-all">
              <User className="w-4 h-4 text-slate-400 fill-slate-400 shrink-0 mr-2.5" />
              <input
                className="w-full text-xs bg-transparent border-0 p-0 text-slate-800 placeholder-slate-400 focus:ring-0 focus:outline-none"
                id="full-name"
                placeholder="Enter your full name"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>
          </div>

          {/* Address */}
          <div className="space-y-1.5" data-purpose="input-address">
            <label
              className="block font-bold text-slate-800 text-xs"
              htmlFor="address"
            >
              Address
            </label>
            <div className="flex items-center border border-slate-200 rounded-xl px-3 py-2.5 bg-white focus-within:ring-2 focus-within:ring-red-500 focus-within:border-transparent transition-all">
              <Home className="w-4 h-4 text-slate-400 fill-slate-400 shrink-0 mr-2.5" />
              <input
                className="w-full text-xs bg-transparent border-0 p-0 text-slate-800 placeholder-slate-400 focus:ring-0 focus:outline-none"
                id="address"
                placeholder="Enter your address"
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
              />
            </div>
          </div>

          {/* City */}
          <div className="space-y-1.5" data-purpose="input-city">
            <label
              className="block font-bold text-slate-800 text-xs"
              htmlFor="city"
            >
              City
            </label>
            <div className="flex items-center border border-slate-200 rounded-xl px-3 py-2.5 bg-white focus-within:ring-2 focus-within:ring-red-500 focus-within:border-transparent transition-all">
              <MapPin className="w-4 h-4 text-slate-400 fill-slate-400 shrink-0 mr-2.5" />
              <input
                className="w-full text-xs bg-transparent border-0 p-0 text-slate-800 placeholder-slate-400 focus:ring-0 focus:outline-none"
                id="city"
                placeholder="Enter your city"
                type="text"
                value={city}
                onChange={(e) => setCity(e.target.value)}
              />
            </div>
          </div>

          {/* State */}
          <div className="space-y-1.5" data-purpose="input-state">
            <label
              className="block font-bold text-slate-800 text-xs"
              htmlFor="state-select"
            >
              State
            </label>
            <div className="relative flex items-center border border-slate-200 rounded-xl px-3 py-2.5 bg-white focus-within:ring-2 focus-within:ring-red-500 focus-within:border-transparent transition-all">
              <Landmark className="w-4 h-4 text-slate-400 shrink-0 mr-2.5" />
              <select
                className={`w-full text-xs bg-transparent border-0 p-0 focus:ring-0 focus:outline-none cursor-pointer appearance-none ${
                  stateVal ? 'text-slate-800 font-medium' : 'text-slate-400'
                }`}
                id="state-select"
                value={stateVal}
                onChange={(e) => setStateVal(e.target.value)}
              >
                <option value="" disabled className="text-slate-400">
                  Select your state
                </option>
                <option value="Gujarat">Gujarat</option>
                <option value="Andhra Pradesh">Andhra Pradesh</option>
                <option value="Delhi">Delhi</option>
                <option value="Karnataka">Karnataka</option>
                <option value="Maharashtra">Maharashtra</option>
                <option value="Rajasthan">Rajasthan</option>
                <option value="Tamil Nadu">Tamil Nadu</option>
                <option value="Uttar Pradesh">Uttar Pradesh</option>
                <option value="West Bengal">West Bengal</option>
              </select>
              <ChevronDown className="w-4 h-4 text-slate-400 pointer-events-none absolute right-3" />
            </div>
          </div>

          {/* Verification Checkbox */}
          <div
            className="pt-1 flex items-center space-x-2.5 cursor-pointer"
            onClick={() => setVerified(!verified)}
            data-purpose="verification-checkbox-group"
          >
            <div
              className={`w-5 h-5 rounded-md flex items-center justify-center transition-colors ${
                verified ? 'bg-red-600 text-white' : 'border-2 border-slate-300 bg-white'
              }`}
            >
              {verified && <Check className="w-3.5 h-3.5 stroke-[3]" />}
            </div>
            <span className="text-xs font-medium text-slate-700 select-none">
              I verify my details are correct
            </span>
          </div>

          {/* SEND OTP Button */}
          <div className="pt-2">
            <button
              type="submit"
              disabled={!verified}
              className={`w-full py-3.5 px-5 bg-red-600 hover:bg-red-700 active:scale-[0.99] text-white font-bold text-xs tracking-wider rounded-xl shadow-md shadow-red-200 transition-all flex items-center justify-between ${
                !verified ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
              }`}
              data-purpose="submit-otp-button"
            >
              <span className="flex-1 text-center font-bold tracking-wider uppercase">
                SEND OTP
              </span>
              <ArrowRight className="w-4 h-4 stroke-[2.5]" />
            </button>
          </div>
        </form>
      </div>

      {/* OTP Verification Modal */}
      {showOtpModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
          <div className="bg-white rounded-3xl p-6 max-w-xs w-full text-center shadow-2xl border border-slate-100">
            <div className="w-12 h-12 bg-red-100 text-red-600 rounded-full flex items-center justify-center mx-auto mb-3">
              <Mail className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-slate-900">Enter Gmail Verification Code</h3>
            <p className="text-xs text-slate-500 mt-1">
              6-digit OTP code dispatched to <br />
              <strong className="text-red-600 font-bold">{email || 'sahay1382@gmail.com'}</strong>
            </p>

            {/* OTP Input Fields */}
            <div className="flex justify-center gap-1.5 my-4">
              {otp.map((digit, idx) => (
                <input
                  key={idx}
                  type="text"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => {
                    const newOtp = [...otp];
                    newOtp[idx] = e.target.value;
                    setOtp(newOtp);
                  }}
                  className="w-9 h-11 text-center text-base font-bold border border-slate-200 rounded-xl focus:border-red-500 focus:ring-1 focus:ring-red-500 focus:outline-none"
                />
              ))}
            </div>

            <p className="text-[10px] text-slate-400 mb-4">
              Demo Code: <span className="font-mono font-bold text-slate-600">123456</span> or use real email code
            </p>

            <div className="flex flex-col gap-2">
              <button
                type="button"
                onClick={handleVerifyOtp}
                className="w-full py-3 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold uppercase tracking-wider shadow-md shadow-red-200 cursor-pointer"
              >
                Verify & Enter App
              </button>
              <button
                type="button"
                onClick={() => setShowOtpModal(false)}
                className="w-full py-2 text-slate-500 text-xs font-medium hover:text-slate-800 cursor-pointer"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
};

