using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Agilent.SignalStudio.Wlan11be;

namespace WlanBE
{
    class Program
    {
        static void Main(string[] args)
        {
            var api = new Agilent.SignalStudio.N7617.Wlan11beAPI();
            api.SetWlan11beFunction(Agilent.SignalStudio.N7617.Mimo11beFunction.MIMO_MxN_1SG);

            api.WaveformSetup.OversamplingRatio = 2;
            api.WaveformSetup.HeadIdleInterval = 1e-6;
            api.WaveformSetup.OfdmaCarrierConfig.EHTLTFType = EHTLTFSymbolIntervalMode.SI_Quadruple;
            api.WaveformSetup.OfdmaCarrierConfig.MaximumPEDuration = MaxPEDurationMode.PE_8;
            api.WaveformSetup.OfdmaCarrierConfig.Link = LinkDirection.Uplink;

            int[] bw_list = { 20, 40, 80, 160, 320 };
            
            foreach (var bw in bw_list)
            {
                api.WaveformSetup.Bandwidth = ConvertBw(bw);
                for (int mcs=0; mcs<=13; mcs++)
                {
                    api.WaveformSetup.OfdmaCarrierConfig.RUSetups[0].UserSetups[0].McsIndex = mcs;

                    MpduSetup mpdu = new MpduSetup();

                    mpdu.DataLength = 4096;
                    mpdu.MacFcs = true;
                    mpdu.MacHeader.Enable = true;
                    mpdu.MacHeader.MacHeaderType = Agilent.SignalStudio.N7617.MacHeaderType.General;

                    MpduSetupList mpdulist = new MpduSetupList();
                    do
                    {
                        mpdulist.Add(mpdu);
                        api.WaveformSetup.OfdmaCarrierConfig.RUSetups[0].UserSetups[0].MpduSetups = mpdulist;  
                    } while (api.WaveformSetup.Nsym < 5);
                    api.Generate();

                    var filename = String.Format("./WLAN_EHT{0}_MCS{1}_KS.wfm", bw, mcs);
                    api.ExportWaveform(filename);
                }
            }
        }

        static Bandwidth ConvertBw(int bw)
        {
            switch (bw)
            { 
                case 20:
                    return Bandwidth.Bandwidth_20MHz;
                case 40:
                    return Bandwidth.Bandwidth_40MHz;
                case 80:
                    return Bandwidth.Bandwidth_80MHz;
                case 160:
                    return Bandwidth.Bandwidth_160MHz;
                case 320:
                    return Bandwidth.Bandwidth_320MHz;
                default:
                    break;
            }
            return Bandwidth.Bandwidth_20MHz;
        }
    }
}
